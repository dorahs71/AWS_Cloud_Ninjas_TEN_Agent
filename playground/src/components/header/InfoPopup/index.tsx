import { useAppSelector } from "@/common"
import styles from "./index.module.scss"

const InfoPopup = () => {
    const options = useAppSelector(state => state.global.options)
    const { channel, userId } = options
    const roomConnected = useAppSelector(state => state.global.roomConnected)
    const agentConnected = useAppSelector(state => state.global.agentConnected)

    return (
        <div className={styles.infoPopup}>
            {/* Info Section */}
            <section className={styles.section}>
                <div className={styles.sectionTitle}>INFO</div>
                <div className={styles.item}>
                    <span className={styles.label}>Room</span>
                    <span className={styles.value}>{channel}</span>
                </div>
                <div className={styles.item}>
                    <span className={styles.label}>Participant</span>
                    <span className={styles.value}>{userId}</span>
                </div>
            </section>

            {/* Status Section */}
            <section className={styles.section}>
                <div className={styles.sectionTitle}>STATUS</div>
                <div className={styles.item}>
                    <div className={styles.label}>Room connected</div>
                    <div className={styles.value}>{roomConnected ? "TRUE" : "FALSE"}</div>
                </div>
                <div className={styles.item}>
                    <div className={styles.label}>Agent connected</div>
                    <div className={styles.value}>{agentConnected ? "TRUE" : "FALSE"}</div>
                </div>
            </section>
        </div>
    )
}

export default InfoPopup
