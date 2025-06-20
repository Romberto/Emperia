import React from 'react';
import styled from './ExitButton.module.css'

export const ExitButton: React.FC = () => {
  return (
    <button className={styled.exit_button}>
        Выйти
    </button>
  );
};
