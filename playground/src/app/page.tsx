"use client"

import { useMemo, useState, useRef, useEffect } from "react"
import dynamic from "next/dynamic"
import Chat from "@/components/chat"
import AuthInitializer from "@/components/authInitializer"
import Menu from "@/components/menu"
import { getRandomUserId, getRandomChannel, useAppDispatch, useSmallScreen, useAppSelector } from "@/common"
import { setOptions } from "@/store/reducers/global"
import styles from "./index.module.scss"

const Rtc = dynamic(() => import("@/components/rtc"), {
  ssr: false,
})
const Header = dynamic(() => import("@/components/header"), {
  ssr: false,
})

export default function Home() {
  const dispatch = useAppDispatch()
  const chatItems = useAppSelector(state => state.global.chatItems)
  const wrapperRef = useRef<HTMLDivElement | null>(null)
  const [activeMenu, setActiveMenu] = useState("Chat")
  const { isSmallScreen } = useSmallScreen()

  useEffect(() => {
    // Set default user on initial load
    const defaultUsername = "DefaultUser"
    const userId = getRandomUserId()
    dispatch(setOptions({
      userName: defaultUsername,
      channel: getRandomChannel(),
      userId
    }))
  }, [dispatch])

  useEffect(() => {
    if (!wrapperRef.current) {
      return
    }
    if (!isSmallScreen) {
      return
    }
    wrapperRef.current.scrollTop = wrapperRef.current.scrollHeight
  }, [isSmallScreen, chatItems])

  const onMenuChange = (item: string) => {
    setActiveMenu(item)
  }

  return (
    <AuthInitializer>
      <main className={styles.home}>
        <Header></Header>
          <div>
            <Rtc></Rtc>    
          </div>
      </main>
    </AuthInitializer>
  )
}
