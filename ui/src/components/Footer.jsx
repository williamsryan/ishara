import React from "react";

const Footer = () => {
    return (
        <footer style={styles.footer}>
            <p style={styles.text}>© {new Date().getFullYear()} Assertion Labs. All rights reserved.</p>
        </footer>
    );
};

const styles = {
    footer: {
        backgroundColor: "#1e293b", // Dark background
        color: "white",
        padding: "10px 20px",
        textAlign: "center",
        borderTop: "2px solid #334155",
    },
    text: {
        margin: 0,
        fontSize: "0.9rem",
    },
};

export default Footer;
