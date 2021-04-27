import EditGroup from "./EditGroup";
import React, {useEffect, useState} from "react";
import {Button, Card, Form, Modal} from "react-bootstrap";
import {Link, useHistory} from "react-router-dom";
import {useStoreActions, useStoreState} from "easy-peasy";
import {FaPlus, FaRegComments} from "react-icons/fa";
import {EE} from "../redux/ws";
import {spinner, timeAgo} from "../utils";
import Error from "../Error";
import ReactMarkdown from "react-markdown";
import Group from "./Group";
import _ from 'lodash'
import moment from 'moment'
import {FaUsers} from "react-icons/all";

export function GroupModal({show, close, gid}) {
  const history = useHistory()
  const emit = useStoreActions(a => a.ws.emit)
  const group = useStoreState(s => s.ws.data['groups/groups/get']?.obj?.[gid])

  function joinGroup() {
    emit(['groups/group/join', {id: gid}])
    history.push('/groups/' + gid)
  }

  return <>
    <Modal
      show={show}
      size='xl'
      onHide={close}
      scrollable={true}
      keyboard={false}
      backdrop='static'
    >
      <Modal.Header closeButton>
        <Modal.Title>{group.title}</Modal.Title>
      </Modal.Header>

      <Modal.Body>
        <div><FaUsers /> {group.n_members} members</div>
        <div>
          <span><FaRegComments /> {group.n_messages} messages</span>
          <small className='muted ml-2'>({timeAgo(group.last_message)})</small>
        </div>
        <hr />

        <div>
          <Card.Title>Description</Card.Title>
          <div className='ml-2'>{group.text_short}</div>
        </div>
        {group.text_long?.length ? <div>
          <hr />
          <Card.Title>About</Card.Title>
          <div className='ml-2'>
            <ReactMarkdown source={group.text_long} linkTarget='_blank' />
          </div>
        </div> : null}
        <Button variant='primary' onClick={joinGroup}>Join Group</Button>
      </Modal.Body>
    </Modal>
  </>
}

export default function AllGroups() {
  const groups = useStoreState(s => s.ws.data['groups/groups/get'])
  const [showCreate, setShowCreate] = useState(false)
  const [showGroup, setShowGroup] = useState(null)

  const {arr, obj} = groups
  if (!arr?.length) {return null}

  function close() {setShowGroup(null)}

  function renderGroup(gid) {
    const g = obj[gid]
    if (!g) {return null}
    return <div key={gid}>
      <Card className='mb-2 cursor-pointer' onClick={() => setShowGroup(gid)}>
        <Card.Body>
          <Card.Title className='mb-2'>
            {g.title}
          </Card.Title>
          <div><FaUsers /> {g.n_members} members</div>
          <div>
            <span><FaRegComments /> {g.n_messages} messages</span>
            <small className='muted ml-2'>({timeAgo(g.last_message)})</small>
          </div>
          <hr />
          <div className='text-muted'>{g.text_short}</div>
        </Card.Body>
      </Card>
    </div>
  }

  return <div>
    {showGroup && <GroupModal show={true} close={close} gid={showGroup} />}
    <EditGroup
      close={() => setShowCreate(false)}
      show={showCreate}
    />
    <Button
      variant='primary'
      className='mb-2'
      onClick={() => setShowCreate(true)}
    >
      <FaPlus /> Create Group
    </Button>
    {arr.map(renderGroup)}
  </div>
}