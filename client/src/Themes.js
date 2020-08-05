import React, {useEffect, useState} from "react"
import {AiStatusMsg, sent2face, spinner, trueKeys} from "./utils"
import {Button, Card, Form} from "react-bootstrap"
import _ from "lodash"
import ForXDays from "./ForXDays"

export default function Themes({fetch_, as, tags, aiStatus}) {
  const [topics, setTopics] = useState({})
  const [fetching, setFetching] = useState(false)
  const [notShared, setNotShared] = useState(false)
  const [form, setForm] = useState({days: 200})

  const fetchTopics = async () => {
    setFetching(true)
    const tags_ = trueKeys(tags)
    const body = {...form}
    if (tags_.length) { body['tags'] = tags_}
    const {data, code, message} = await fetch_('themes', 'POST', body)
    setFetching(false)
    if (code === 401) {return setNotShared(message)}
    setTopics(data)
  }

  if (notShared) {return <h5>{notShared}</h5>}

  return <>
    <Form onSubmit={_.noop}>
    <ForXDays
      form={form}
      setForm={setForm}
      feature={'themes'}
    />

    {fetching ? <>
      <div>{spinner}</div>
      <Form.Text muted>Takes a long time. Will fix later.</Form.Text>
    </> : <>
      <Button
        disabled={aiStatus !== 'on'}
        className='bottom-margin'
        variant='primary'
        onClick={fetchTopics}
      >Show Themes</Button>
      <AiStatusMsg status={aiStatus} />
    </>}
    </Form>
    {_.size(topics) > 0 && <hr/>}
    {_.map(topics, (obj, topic)=>(
      <Card key={topic} className='bottom-margin'>
        <Card.Body>
          <Card.Title>{obj.n_entries} Entries</Card.Title>
          {/*<Card.Subtitle className="mb-2 text-muted">Card Subtitle</Card.Subtitle>*/}
          <Card.Text>
            {sent2face(obj.sentiment)}
            {obj.terms.join(', ')}

            {obj.summary && <p><hr/><b>Summary</b>: {obj.summary}</p>}
          </Card.Text>
        </Card.Body>
      </Card>
    ))}
  </>
}
