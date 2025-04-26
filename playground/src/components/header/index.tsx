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
import { useState } from "react"

const Header = () => {
  const [settingsOpen, setSettingsOpen] = useState(false)

  const channelNameText = 'Cloud Ninjas'

  const onClickGithub = () => {
    if (typeof window !== "undefined") {
      window.open(GITHUB_URL, "_blank")
    }
  }

  return <div className={styles.header}>
    <span className={styles.content}>{channelNameText}</span>
    <div className={styles.rightSection}>
      <span onClick={onClickGithub} className={styles.githubWrapper}>
        <GithubIcon></GithubIcon>
      </span>
      <Network></Network>
      <span className={styles.iconWrapper} onClick={() => setSettingsOpen(true)}>
        <SettingOutlined />
      </span>
      <ConnectButton />
    </div>
    <SettingsDialog open={settingsOpen} onClose={() => setSettingsOpen(false)} />
  </div>
}


export default Header
