import pdb, logging, asyncio
import common.models as M
from app.socketio import sio, redis, on_
from app.utils import getuser

logger = logging.getLogger(__name__)

S = "server/groups"
C = "client/groups"

# 835723e9: leave other rooms on group.enter, and get gid for leave/join from sid.rooms
async def get_gid(sid):
    sess = await sio.get_session(sid)
    return sess['gid']


async def send_message(msg, sess):
    msg = M.Message(**msg)
    sess.add(msg)
    sess.commit()
    gid = str(msg.group_id)
    msg = dict(
        message=msg.text,
        id=str(msg.owner_id) if msg.owner_id else None,
    )
    await sio.emit("client/groups/message", msg, room=gid)


@on_(f"{S}/messages.post")
async def on_messages_post(sid, data: M.SIMessage, d):
    gid = await get_gid(sid)
    msg = dict(
        text=data['message'],
        group_id=gid,
        owner_id=d.uid,
        recipient_type=M.MatchTypes.groups,
    )
    await send_message(msg, d.sess)


@on_(f"{S}/group.join")
async def on_group_join(sid, data, d):
    gid = await get_gid(sid)
    uid = str(d.uid)
    ug = M.Group.join_group(d.sess, gid, uid)
    if not ug: return {}
    msg = dict(
        group_id=gid,
        recipient_type=M.MatchTypes.groups,
        text=f"{ug.username} just joined!"
    )
    asyncio.ensure_future(send_message(msg, d.sess))
    asyncio.ensure_future(get_members(sid, gid, d))


@on_(f"{S}/group.leave")
async def on_group_leave(sid, data, d):
    gid = await get_gid(sid)
    uid = str(d.uid)
    ug = M.Group.leave_group(d.sess, gid, uid)
    msg = dict(
        group_id=gid,
        recipient_type=M.MatchTypes.groups,
        text=f"{ug['username']} just left :("
    )
    asyncio.ensure_future(get_members(sid, gid, d))
    asyncio.ensure_future(send_message(msg, d.sess))


@on_(f"{S}/group.enter")
async def on_group_enter(sid, gid, d):
    sess = await sio.get_session(sid)
    sess['gid'] = gid
    await sio.save_session(sid, sess)
    sio.enter_room(sid, gid)

    # skipping await statements, so we can just shove things down the pipe
    
    # await refresh_online(gid)
    # await get_members(sid, gid, d)
    asyncio.ensure_future(refresh_online(gid))
    asyncio.ensure_future(get_members(sid, gid, d))

    # Fetch group
    group = d.sess.query(M.Group).get(gid)
    group = group.to_json()
    asyncio.ensure_future(
        sio.emit(f"{C}/group", group, sid=sid, gid=gid)
    )

    messages = d.sess.query(M.Message) \
        .filter(M.Message.group_id == gid) \
        .order_by(M.Message.created_at.asc()) \
        .all()
    messages = [dict(
        id=str(m.owner_id),
        message=m.text,
    ) for m in messages]
    asyncio.ensure_future(
        sio.emit(f"{C}/messages", messages, sid=sid, gid=gid)
    )


@on_(f"{S}/groups.get")
async def on_groups_get(sid, data, d):
    groups = d.sess.query(M.Group).all()
    groups = [g.to_json() for g in groups]
    await sio.emit(f"{C}/groups", groups, sid=sid)


@on_(f"{S}/members.get")
async def on_members_get(sid, gid, d):
    await get_members(sid, gid, d)


async def get_members(sid, gid, d):
    members = M.UserGroup.get_members(d.sess, gid)
    await sio.emit(f"{C}/members", members, room=gid)


async def refresh_online(gid):
    sids = redis.get_participants('/', gid)
    uids = {}
    for s in next(sids):
        try:
            sess = await sio.get_session(s)
            uids[sess['uid']] = True
        except: continue
    await sio.emit(f"{C}/online", uids, room=gid)


@on_(f"{S}/privacy.put", viewer=False)
async def on_privacy_put(sid, data, d):
    sess = await sio.get_session(sid)
    uid, gid = sess['uid'], data['gid']
    ug = d.sess.query(M.UserGroup)\
            .filter_by(user_id=uid, group_id=gid).first()
    setattr(ug, data['key'], data['value'])
    d.sess.commit()
    await get_members(sid, gid, d)


@on_(f"{S}/groups.post")
async def on_groups_post(sid, data, d):
    group = M.Group.create_group(d.sess, data["title"], data["text"], d.uid, data["privacy"])
    return group.to_json()


groups_router = None