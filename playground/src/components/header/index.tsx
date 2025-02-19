"use client"

import { useAppSelector, GITHUB_URL, useSmallScreen } from "@/common"
import Network from "./network"
import { GithubIcon, LogoIcon } from "@/components/icons"
import { InfoCircleOutlined, QuestionCircleOutlined, SettingOutlined } from "@ant-design/icons"
import { Popover } from "antd"
import InfoPopup from "./InfoPopup"
import DescriptionPopup from "./DescriptionPopup"
import SettingsDialog from "./SettingsDialog"
import ConnectButton from "./ConnectButton"

import styles from "./index.module.scss"
import { useMemo, useState } from "react"

const Header = () => {
  const options = useAppSelector(state => state.global.options)
  const { channel } = options
  const { isSmallScreen } = useSmallScreen()
  const [settingsOpen, setSettingsOpen] = useState(false)

  const channelNameText = useMemo(() => {
    return !isSmallScreen ? `Channel Name：${channel}` : channel
  }, [isSmallScreen, channel])

  const onClickGithub = () => {
    if (typeof window !== "undefined") {
      window.open(GITHUB_URL, "_blank")
    }
  }

  return <div className={styles.header}>
    <span className={styles.logoWrapper}>
      <LogoIcon></LogoIcon>
    </span>
    <span className={styles.content}>{channelNameText}</span>
    <div className={styles.rightSection}>
      <span onClick={onClickGithub} className={styles.githubWrapper}>
        <GithubIcon></GithubIcon>
      </span>
      <Network></Network>
      <Popover content={<InfoPopup />} trigger="click" placement="bottom">
        <span className={styles.iconWrapper}>
          <InfoCircleOutlined />
        </span>
      </Popover>
      <Popover content={<DescriptionPopup />} trigger="click" placement="bottom">
        <span className={styles.iconWrapper}>
          <QuestionCircleOutlined />
        </span>
      </Popover>
      <span className={styles.iconWrapper} onClick={() => setSettingsOpen(true)}>
        <SettingOutlined />
      </span>
      <ConnectButton />
    </div>
    <SettingsDialog open={settingsOpen} onClose={() => setSettingsOpen(false)} />
  </div>
}


export default Header
