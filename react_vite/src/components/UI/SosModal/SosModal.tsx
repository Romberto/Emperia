import styled from "./SosModal.module.css";
export const SosModal: React.FC<{
  onClose: () => void;
  onSelect: (type: string) => void;
}> = ({ onClose, onSelect }) => {
  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // Если клик был по overlay (а не по вложенной модалке)
    if (e.target === e.currentTarget) {
      onClose();
    }
  };
  return (
    <div className={styled.modalOverlay} onClick={handleOverlayClick}>
      <div className={styled.modal}>
        <h2>Выберите ситуацию</h2>
        <button onClick={() => onSelect("dtp")}>Попал в ДТП</button>
        <button onClick={() => onSelect("conflict")}>
          Конфликтная ситуация
        </button>
        <button onClick={onClose}>Отмена</button>
      </div>
    </div>
  );
};
