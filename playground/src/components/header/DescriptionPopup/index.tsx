import { DESCRIPTION } from "@/common"
import styles from "./index.module.scss"

const DescriptionPopup = () => {
    return (
        <div className={styles.descriptionPopup}>
            <div className={styles.title}>DESCRIPTION</div>
            <div className={styles.content}>{DESCRIPTION}</div>
        </div>
    )
}

export default DescriptionPopup
