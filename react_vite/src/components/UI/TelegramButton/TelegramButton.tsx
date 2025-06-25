import React, { useEffect, useRef } from "react";

type TelegramUser = {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
};

type TelegramLoginProps = {
  botName: string;
  onAuth: (user: TelegramUser) => void;
  buttonSize?: "large" | "medium" | "small";
  cornerRadius?: number;
  requestAccess?: "write" | "read";
};

const TelegramButton: React.FC<TelegramLoginProps> = ({
  botName,
  onAuth,
  buttonSize = "medium",
  cornerRadius = 10,
  requestAccess = "write",
}) => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!botName || !ref.current) return;

    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?7";
    script.setAttribute("data-telegram-login", botName);
    script.setAttribute("data-size", buttonSize);
    script.setAttribute("data-radius", cornerRadius.toString());
    script.setAttribute("data-request-access", requestAccess);
    script.setAttribute("data-userpic", "true");
    script.setAttribute("data-onauth", "onTelegramAuth(user)");
    script.async = true;

    (window as any).onTelegramAuth = (user: TelegramUser) => {
      onAuth(user);
    };

    ref.current.innerHTML = ""; // Очистка перед вставкой
    ref.current.appendChild(script);

    return () => {
      delete (window as any).onTelegramAuth;
    };
  }, [botName, onAuth, buttonSize, cornerRadius, requestAccess]);

  return <div ref={ref} />;
};

export default TelegramButton;
