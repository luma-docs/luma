import styles from "./Footer.module.css";

export function Footer() {
  return (
    <footer className={styles.footer}>
      <a
        href="https://luma-docs.org"
        target="_blank"
        rel="noopener noreferrer"
        className={styles.link}
      >
        Made with Luma
      </a>
    </footer>
  );
}
