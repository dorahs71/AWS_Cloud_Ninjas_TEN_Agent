import { useState, useEffect } from "react"
import { Modal, Tabs, Select, Checkbox, Input } from "antd"
import {
    LANG_OPTIONS,
    VOICE_OPTIONS,
    MODE_OPTIONS,
    GRAPH_NAME_OPTIONS,
    useAppSelector
} from "@/common"
import styles from "./index.module.scss"

const { TextArea } = Input
const { TabPane } = Tabs

const SettingsDialog = ({ open, onClose }: { open: boolean; onClose: () => void }) => {
    const agentConnected = useAppSelector(state => state.global.agentConnected)

    const [mode, setMode] = useState("chat")
    const [graphName, setGraphName] = useState(GRAPH_NAME_OPTIONS[0]['value'])
    const [lang, setLang] = useState(LANG_OPTIONS[0]['value'])
    const [outputLanguage, setOutputLanguage] = useState(lang)
    const [partialStabilization, setPartialStabilization] = useState(false)
    const [voice, setVoice] = useState("male")
    const [greeting, setGreeting] = useState("")
    const [systemPrompt, setSystemPrompt] = useState("")

    // Load initial settings from localStorage
    useEffect(() => {
        const storedSettings = localStorage.getItem('astra-settings')
        if (storedSettings) {
            const settings = JSON.parse(storedSettings)
            setMode(settings.mode || "chat")
            setGraphName(settings.graphName || GRAPH_NAME_OPTIONS[0]['value'])
            setLang(settings.lang || LANG_OPTIONS[0]['value'])
            setOutputLanguage(settings.outputLanguage || lang)
            setPartialStabilization(settings.partialStabilization || false)
            setVoice(settings.voice || "male")
            setGreeting(settings.greeting || "")
        }
    }, [])

    // Save settings and dispatch event whenever they change
    useEffect(() => {
        const settings = {
            mode,
            graphName,
            lang,
            outputLanguage,
            partialStabilization,
            voice,
            greeting
        }
        localStorage.setItem('astra-settings', JSON.stringify(settings))

        // Dispatch custom event for real-time updates
        const event = new CustomEvent('astra-settings-changed', { detail: settings })
        window.dispatchEvent(event)
    }, [mode, graphName, lang, outputLanguage, partialStabilization, voice, greeting])

    return (
        <Modal
            title="Settings"
            open={open}
            onCancel={onClose}
            footer={null}
            width={600}
            className={styles.settingsDialog}
        >
            <Tabs defaultActiveKey="general">
                <TabPane tab="General" key="general">
                    <div className={styles.settingGroup}>
                        <div className={styles.settingItem}>
                            <div className={styles.label}>GRAPH NAME</div>
                            <Select
                                disabled={agentConnected}
                                className={`${styles.select} dark`}
                                value={graphName}
                                options={GRAPH_NAME_OPTIONS}
                                onChange={v => setGraphName(v)}
                            />
                        </div>

                        <div className={styles.settingItem}>
                            <div className={styles.label}>AGENT MODE</div>
                            <Select
                                disabled={agentConnected}
                                className={`${styles.select} dark`}
                                value={mode}
                                options={MODE_OPTIONS}
                                onChange={v => setMode(v)}
                            />
                        </div>

                        <div className={styles.settingItem}>
                            <div className={styles.label}>INPUT LANGUAGE</div>
                            <Select
                                disabled={agentConnected}
                                className={`${styles.select} dark`}
                                value={lang}
                                options={LANG_OPTIONS}
                                onChange={v => {
                                    setLang(v)
                                    if (mode == "chat") {
                                        setOutputLanguage(v)
                                    }
                                }}
                            />
                        </div>

                        {mode == "translate" && (
                            <>
                                <div className={styles.settingItem}>
                                    <div className={styles.label}>OUTPUT LANGUAGE</div>
                                    <Select
                                        disabled={agentConnected}
                                        className={`${styles.select} dark`}
                                        value={outputLanguage}
                                        options={LANG_OPTIONS}
                                        onChange={v => setOutputLanguage(v)}
                                    />
                                </div>

                                <div className={styles.settingItem}>
                                    <div className={styles.label}>ASR PARTIAL STABILIZATION</div>
                                    <Checkbox
                                        disabled={agentConnected}
                                        className={`${styles.checkbox} dark`}
                                        checked={partialStabilization}
                                        onChange={e => setPartialStabilization(e.target.checked)}
                                    >
                                        Enable(May reduce accuracy)
                                    </Checkbox>
                                </div>
                            </>
                        )}

                        <div className={styles.settingItem}>
                            <div className={styles.label}>VOICE</div>
                            <Select
                                disabled={agentConnected}
                                value={voice}
                                className={`${styles.select} dark`}
                                options={VOICE_OPTIONS}
                                onChange={v => setVoice(v)}
                            />
                        </div>
                    </div>
                </TabPane>

                <TabPane tab="Prompt" key="prompt">
                    <div className={styles.settingGroup}>
                        <div className={styles.settingItem}>
                            <div className={styles.label}>GREETING</div>
                            <TextArea
                                className={`${styles.textarea} dark`}
                                disabled={agentConnected}
                                value={greeting}
                                placeholder="Enter a greeting message"
                                onChange={e => setGreeting(e.target.value)}
                            />
                        </div>

                        <div className={styles.settingItem}>
                            <div className={styles.label}>SYSTEM PROMPT</div>
                            <TextArea
                                className={`${styles.textarea} dark`}
                                disabled={agentConnected}
                                value={systemPrompt}
                                placeholder="Customize system prompt, leave blank to use default"
                                onChange={e => setSystemPrompt(e.target.value)}
                            />
                        </div>
                    </div>
                </TabPane>

                <TabPane tab="Reserved 1" key="reserved1">
                    <div className={styles.emptyTab}>Reserved for future use</div>
                </TabPane>

                <TabPane tab="Reserved 2" key="reserved2">
                    <div className={styles.emptyTab}>Reserved for future use</div>
                </TabPane>
            </Tabs>
        </Modal>
    )
}

export default SettingsDialog
