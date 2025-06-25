import React, { useState } from "react";
import styled from "./Content.module.css";
import { Button } from "../Button/Button";
import { SOSButton } from "../SOSButton/SOSButton";
import { useAppSelector } from "../../../hook/useAppSelector";
import { SosModal } from "../SosModal/SosModal";

export const Content: React.FC = () => {
  const { username } = useAppSelector((state) => state.auth);
  const [isModalOpen, setIsModalOpen] = useState(false);
    const handleSOSClick = (e: React.MouseEvent) => {
    e.preventDefault(); 
    setIsModalOpen(true);
  };
    const handleSelect = (type: string) => {
    setIsModalOpen(false);
    console.log("Выбран вариант:", type);
    // Здесь можно отправить данные, редиректить и т.д.
  };
  return (
    <>
      <ul className={styled.content}>
        <li>
          <a
            href="https://t.me/iwmcc64"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Button variant="white" fontSize={20}>
              Чат (болталка)
            </Button>
          </a>
        </li>
        <li>
          <a
            href="https://t.me/promoto64"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Button variant="white" fontSize={20}>
              Наш телеграмм канал
            </Button>
          </a>
        </li>

        {/*<li><Link to={'/servisec'}><Button variant="white" fontSize={20}>Услуги</Button></Link></li>
           <li><Link to={'/sales'}><Button variant="white" fontSize={20}>Объявления</Button></Link></li>*/}
        <li>
          {username && (
            <a href="#" onClick={handleSOSClick}>
              <SOSButton />
            </a>
          )}       
        </li>
      </ul>
      {isModalOpen && <SosModal onClose={() => setIsModalOpen(false)} onSelect={handleSelect} />}
    </>
  );
};
