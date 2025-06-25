// Header.tsx

import { useAppDispatch } from "../../../hook/useAppDispatch"; // создадим ниже
import styled from "./Header.module.css";
import logo from "../../../assets/logo-moto.svg";
import { setUser } from "../../../features/auth/authSlice";
import {
  useLoginTelegramMutation,
  type TelegramAuthPayload,
} from "../../../features/auth/authApi";
import TelegramButton from "../TelegramButton/TelegramButton";
import { useAppSelector } from "../../../hook/useAppSelector";
import { getCityFromLocation } from "../../../features/geo/geolocation";
import { useEffect, useState } from "react";

export const Header: React.FC = () => {
  const [city, setSity] = useState("");
  const dispatch = useAppDispatch();
  useEffect(() => {
    const fetchLocation = async () => {
      const location = await getCityFromLocation();

      if (location.error) {
        console.error("Ошибка геолокации:", location.error);
      } else {
        {
          location.city &&
            (localStorage.setItem("city", location.city),
            setSity(location.city));
        }
      }
    };
    fetchLocation();
  }, []);
  const { username, first_name, photo_url } = useAppSelector(
    (state) => state.auth
  );
  const [loginTelegram] = useLoginTelegramMutation();

  const handleTelegramAuth = async (user: TelegramAuthPayload) => {
    try {
      const {
        id,
        first_name,
        last_name,
        username,
        photo_url,
        auth_date,
        hash,
      } = user;

      const payload = {
        id,
        first_name,
        last_name,
        username,
        photo_url,
        auth_date,
        hash,
      };

      const { access_token, refresh_token } = await loginTelegram(
        payload
      ).unwrap();

      localStorage.setItem("access_token", access_token);
      localStorage.setItem("tg_first_name", first_name);
      localStorage.setItem("refresh_token", refresh_token);
      {
        username && localStorage.setItem("username", username);
      }
      {
        photo_url && localStorage.setItem("tg_photo_url", photo_url);
      }
      dispatch(setUser({ username, first_name, photo_url }));
    } catch (err) {
      console.error("Ошибка авторизации:", err);
    }
  };
  return (
    <header className={styled.header}>
      <a href="#">
        <img className={styled.logo__img} src={logo} alt="Логотип" />
      </a>
      <div className={styled.auth}>
        {!username ? (
          <TelegramButton
            botName="SimplyMenuBot"
            onAuth={handleTelegramAuth}
            requestAccess="write"
          />
        ) : (
          <div className={styled.user}>
            {photo_url && (
              <img src={photo_url} alt="avatar" className={styled.avatar} />
            )}
            <span>{first_name || username}</span>
            <span>{city}</span>
          </div>
        )}
      </div>
    </header>
  );
};
