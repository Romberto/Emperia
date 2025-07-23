import React from "react";
import { Button } from "../Button/Button";
import styled from './SOSButton.module.css'

export const SOSButton: React.FC<{ username?: string }> = ({ username }) => {
  const sendSOS = async () => {
    if (!navigator.geolocation) {
      alert("Геолокация не поддерживается браузером.");
      return;
    }
    if (!username) {
      /* здесь нужна функция  */

      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;

        const payload = {
          username,
          lat: latitude,
          lng: longitude,
        };
        console.log(payload);
        try {
          const response = await fetch("/api/sos", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });

          if (response.ok) {
            alert("Сообщение отправлено.");
          } else {
            alert("Ошибка при отправке SOS.");
          }
        } catch (err) {
          alert("Ошибка соединения с сервером.");
        }
      },
      () => {
        alert("Не удалось определить местоположение.");
      }
    );
  };

  return (
    <div className={styled.gradient_glow}>
      <Button variant="bighelp" fontSize={60} onClick={sendSOS}>
        <span>Moto</span>
        <span style={{ color: "var(--orange)" }}>HELP</span>
      </Button>
    </div>
  );
};
