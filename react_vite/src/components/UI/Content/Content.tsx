import React from 'react';
import styled from './Content.module.css'
import { Button } from '../Button/Button';
import { Link } from 'react-router'

export const Content: React.FC = () => {
  return (
    <>
        <ul className={styled.content}>
            <li><Link to={'/festivals'}><Button variant="white" fontSize={20}>Фестивали</Button></Link></li>
            <li><Link to={'/help'}><Button variant="white" fontSize={20}>ТехПомощь</Button></Link></li>
            <li><Link to={'/servisec'}><Button variant="white" fontSize={20}>Услуги</Button></Link></li>
            <li><Link to={'/sales'}><Button variant="white" fontSize={20}>Объявления</Button></Link></li>
            <li><Link to={'/sos'}><Button variant="red" fontSize={20}>SOS</Button></Link></li>

        </ul>
    </>
  );
};
