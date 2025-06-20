// Header.tsx

import { useDispatch } from "react-redux";// создадим ниже
import styled from "./Header.module.css";
import  logo  from "../../../assets/moto.png";
import { setUser } from "../../../features/auth/authSlice";
import { useLoginTelegramMutation, type TelegramAuthPayload } from "../../../features/auth/authApi";
import TelegramLoginButton from "../TelegramButton/TelegramButton";

export const Header: React.FC = () => {
  const [loginTelegram, { isLoading }] = useLoginTelegramMutation();
  const dispatch = useDispatch();

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

      const { access_token } = await loginTelegram(payload).unwrap();
      localStorage.setItem("access_token", access_token);

      dispatch(setUser({ username })); // сохраним юзернейм в store
    } catch (e) {
      console.error("Ошибка авторизации через Telegram:", e);
    }
  };

  return (
    <header>
      <a href="#">
        <img
          className={styled.logo__img}
          src={logo}
          alt="логотип клуба в виде английских букв I, а так же W"
        />
      </a>
      <div className={styled.auth}>
        {isLoading && <p>Загрузка...</p>}
        <TelegramLoginButton
          botName="SimplyMenuBot"
          onAuth={handleTelegramAuth}
          requestAccess="write"
        />
      </div>
    </header>
  );
};
