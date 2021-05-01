import React, {useEffect, useState} from "react"
import _ from 'lodash'
import ShareForm from './Form'
import {useStoreState, useStoreActions} from 'easy-peasy'
import {EE} from '../../redux/ws'
import {FaPlus, FaRegComments, FaUser} from "react-icons/fa";
import {trueObj} from "../../Helpers/utils";
import {FaArrowLeft} from "react-icons/all";
import {Card, CardContent, Button} from "@material-ui/core";

import {FullScreenDialog} from "../../Helpers/Dialog";
import {DialogContent} from "@material-ui/core";
import {Add, ArrowBack} from "@material-ui/icons";

function Share({s}) {
  let myGroups = useStoreState(s => s.ws.data['groups/mine/get']?.obj)
  const setSharePage = useStoreActions(a => a.user.setSharePage)

  function renderList(icon, arr, map_=_.identity) {
    arr = _.compact(arr)
    if (!arr?.length) {return null}
    return <div>{icon} {arr.map(map_).join(', ')}</div>
  }

  return <Card
    sx={{mb: 2, cursor: 'pointer'}}
    onClick={() => setSharePage({id: s.share.id})}
  >
    <CardContent>
      {renderList(<FaUser />, s?.users)}
      {renderList(<FaRegComments />, s?.groups, id => myGroups[id].title)}
    </CardContent>
  </Card>
}

export default function Sharing() {
  const emit = useStoreActions(a => a.ws.emit)
  const shares = useStoreState(s => s.ws.data['shares/egress/get'])
  const sharePage = useStoreState(s => s.user.sharePage)
  const setSharePage = useStoreActions(a => a.user.setSharePage)

  useEffect(() => {
    emit(['shares/egress/get', {}])
  }, [])

  if (!sharePage) {return null}
  const {arr, obj} = shares

  // be23b9f8: show CantSnoop. New setup uses viewer data where attempting CantSnoop

  // Due to share-merging, sometimes the right share-id isn't present. If they click
  // "modify sharing" on a group with multiple shares, don't know which one to edit,
  // so just list all.
  const isList = sharePage.list || (sharePage.id && !obj?.[sharePage.id])

  if (isList) {
    return <div>
      <Button
        sx={{mb: 2}}
        variant='contained'
        color='primary'
        onClick={() => setSharePage({create: true})}
        startIcon={<Add />}
      >New Share</Button>
      {arr?.map(sid => <Share key={sid} s={obj[sid]}/>)}
    </div>
  }

  return <div>
    <Button
      variant={false}
      size='small'
      onClick={() => setSharePage({list: true})}
      startIcon={<ArrowBack />}
    >
      List Shares
    </Button>
    {sharePage.create ? <ShareForm />
      : sharePage.id ? <ShareForm s={obj[sharePage.id]} />
      : null}
  </div>
}

export function SharingModal() {
  const sharePage = useStoreState(s => s.user.sharePage)
  const setSharePage = useStoreActions(a => a.user.setSharePage)

  function close() {
    setSharePage(null)
  }

  return <>
    <FullScreenDialog
      open={sharePage || false}
      onClose={close}
      title='Sharing'
    >
      <DialogContent>
        <Sharing />
      </DialogContent>
    </FullScreenDialog>
  </>
}
