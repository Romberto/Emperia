import React from "react";
import { Button } from "../Button/Button";
import styled from "./SOSButton.module.css";
import { useAppDispatch } from "../../../hook/useAppDispatch";
import { setSosModulOpen } from "../../../features/moduls/modulsSlise";

export const SOSButton: React.FC = () => {

  const dispatch = useAppDispatch()
  return (
    <div className={styled.gradient_glow}>
      <Button variant="bighelp" fontSize={60} onClick={()=> dispatch(setSosModulOpen())}>
        <span>Moto</span>
        <span style={{ color: "var(--orange)" }}>HELP</span>
      </Button>
    </div>
  );
};
