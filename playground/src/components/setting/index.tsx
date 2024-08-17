"use client"

import { setAgentConnected } from "@/store/reducers/global"
import {
  DESCRIPTION, useAppDispatch, useAppSelector, apiPing,
  LANG_OPTIONS, VOICE_OPTIONS, apiStartService, apiStopService,
  MODE_OPTIONS, GRAPH_NAME_OPTIONS
} from "@/common"
import Info from "./Info"
import Status from "./status"
import { Select, Button, message } from "antd"
import StyleSelect from "./themeSelect"
import { useEffect, useState } from "react"
import { LoadingOutlined } from "@ant-design/icons"
import styles from "./index.module.scss"



let intervalId: any

const Setting = () => {
  const dispatch = useAppDispatch()
  const agentConnected = useAppSelector(state => state.global.agentConnected)
  const channel = useAppSelector(state => state.global.options.channel)
  const userId = useAppSelector(state => state.global.options.userId)
  const [mode, setMode] = useState("chat")
  const [graphName, setGraphName] = useState(GRAPH_NAME_OPTIONS[0]['value'])
  const [lang, setLang] = useState("en-US")
  const [outputLanguage, setOutputLanguage] = useState(lang)
  const [voice, setVoice] = useState("male")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (channel) {
      checkAgentConnected()
    }
  }, [channel])


  const checkAgentConnected = async () => {
    const res: any = await apiPing(channel)
    if (res?.code == 0) {
      dispatch(setAgentConnected(true))
    }
  }

  const onClickConnect = async () => {
    if (loading) {
      return
    }
    setLoading(true)
    if (agentConnected) {
      await apiStopService(channel)
      dispatch(setAgentConnected(false))
      message.success("Agent disconnected")
      stopPing()
    } else {
      if (mode == "chat") {
        setOutputLanguage(lang)
      }

      const res = await apiStartService({
        channel,
        userId,
        language: lang,
        voiceType: voice,
        graphName: graphName,
        mode: mode,
        outputLanguage: outputLanguage
      })
      const { code, msg } = res || {}
      if (code != 0) {
        if (code == "10001") {
          message.error("The number of users experiencing the program simultaneously has exceeded the limit. Please try again later.")
        } else {
          message.error(`code:${code},msg:${msg}`)
        }
        setLoading(false)
        throw new Error(msg)
      }
      dispatch(setAgentConnected(true))
      message.success("Agent connected")
      startPing()
    }
    setLoading(false)
  }

  const startPing = () => {
    if (intervalId) {
      stopPing()
    }
    intervalId = setInterval(() => {
      apiPing(channel)
    }, 3000)
  }

  const stopPing = () => {
    if (intervalId) {
      clearInterval(intervalId)
      intervalId = null
    }
  }


  return <section className={styles.setting} >
    {/* description */}
    <section className={styles.description}>
      <div className={styles.title}>DESCRIPTION</div>
      <div className={styles.text}>{DESCRIPTION}</div>
      <div className={`${styles.btnConnect} ${agentConnected ? styles.disconnect : ''}`} onClick={onClickConnect}>
        <span className={`${styles.btnText} ${agentConnected ? styles.disconnect : ''}`}>
          {!agentConnected ? "Connect" : "Disconnect"}
          {loading ? <LoadingOutlined className={styles.loading}></LoadingOutlined> : null}
        </span>
      </div>
    </section>
    {/* info */}
    <Info />
    {/* status */}
    <Status></Status>
    {/* select */}
    <section className={styles.selectWrapper}>
      <div className={styles.title}>GRAPH NAME</div>
      <Select disabled={agentConnected} className={`${styles.select} dark`} value={graphName} options={GRAPH_NAME_OPTIONS} onChange={v => {
        setGraphName(v)
      }}></Select>

      <div className={styles.title}>AGENT MODE</div>
      <Select disabled={agentConnected} className={`${styles.select} dark`} value={mode} options={MODE_OPTIONS} onChange={v => {
        setMode(v)
      }}></Select>

      <div className={styles.title}>INPUT LANGUAGE</div>
      <Select disabled={agentConnected} className={`${styles.select} dark`} value={lang} options={LANG_OPTIONS} onChange={v => {
        setLang(v)

        if (mode == "chat") {
          setOutputLanguage(v)
        }
      }}></Select>

      {/* if mode == translate, show output_language options */}
      {mode == "translate" ? <>
        <div className={styles.title}>OUTPUT LANGUAGE</div>
        <Select disabled={agentConnected} className={`${styles.select} dark`} value={outputLanguage} options={LANG_OPTIONS} onChange={v => {
          setOutputLanguage(v)
        }}></Select>
      </> : null}
    </section>
    <section className={styles.selectWrapper}>
      <div className={styles.title}>Voice</div>
      <Select disabled={agentConnected} value={voice} className={`${styles.select} dark`} options={VOICE_OPTIONS} onChange={v => {
        setVoice(v)
      }}></Select>
    </section>
    {/* style */}
    <StyleSelect></StyleSelect>
  </section>
}


export default Setting
