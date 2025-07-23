import React from "react";
import styles from "./Button.module.css";

type Variant = "black" | "green" | "white" | "red" | 'bighelp';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  children: React.ReactNode;
  fontSize?: number
}

export const Button: React.FC<ButtonProps> = ({
  variant = "black",
  fontSize,
  children,
  style,
  className = "",
  ...props
}) => {
  return (
    <button
      className={`${styles.btn} ${styles[`btn--${variant}`]}`}
      style={{ fontSize: fontSize ? `${fontSize}px` : undefined, ...style }}
      {...props}
    >
      {children}
    </button>
  );
};
