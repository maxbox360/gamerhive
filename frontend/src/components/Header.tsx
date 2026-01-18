"use client";

import React from "react";
import Link from "next/link";

export default function Header() {
  return (
    <header style={{
      backgroundColor: "#000",
      color: "#FFD700", // honey yellow
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      padding: "1rem 2rem",
      fontFamily: "Arial, sans-serif"
    }}>
      <div style={{ fontWeight: "bold", fontSize: "1.5rem" }}>
        GamerHive
      </div>
      <nav style={{ display: "flex", gap: "1.5rem", alignItems: "center" }}>
        <Link href="/signin" style={{ color: "#FFD700", textDecoration: "none" }}>Sign In</Link>
        <Link href="/signup" style={{ color: "#FFD700", textDecoration: "none" }}>Create Account</Link>
        <Link href="/games" style={{ color: "#FFD700", textDecoration: "none" }}>Games</Link>
        <Link href="/lists" style={{ color: "#FFD700", textDecoration: "none" }}>Lists</Link>
        <input
          type="text"
          placeholder="Search games"
          style={{
            padding: "0.3rem 0.5rem",
            borderRadius: "5px",
            border: "1px solid #FFD700",
            backgroundColor: "#222",
            color: "#fff"
          }}
        />
      </nav>
    </header>
  );
}
