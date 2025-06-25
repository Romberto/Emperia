import React from "react";
import styled from "./ExitButton.module.css";
import { useAppDispatch } from "../../../hook/useAppDispatch";
import { logout } from "../../../features/auth/authSlice";

export const ExitButton: React.FC = () => {
  const dispatch = useAppDispatch();

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("tg_username");
    localStorage.removeItem("tg_first_name");
    localStorage.removeItem("tg_photo_url");
    // если есть
    dispatch(logout());
    // window.location.reload(); // по желанию
  };

  return (
    <button className={styled.exit_button} onClick={handleLogout}>
      Выйти
    </button>
  );
};
