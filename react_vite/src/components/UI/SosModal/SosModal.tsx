import type { SosType } from "../Content/types";
import styled from "./SosModal.module.css";
export const SosModal: React.FC<{
  onClose: () => void;
}> = ({ onClose }) => {
      const sendSOS = async (typeSos: SosType) => {
      if (!navigator.geolocation) {
        alert("Геолокация не поддерживается браузером.");
        return;
      }

      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;

          const payload = {
            lat: latitude,
            lng: longitude,
            typeSos: typeSos,
          };
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
        <button onClick={() => sendSOS("dtp")}>Попал в ДТП</button>
        <button onClick={() => sendSOS("conflict")}>
          Конфликтная ситуация
        </button>
        <button onClick={onClose}>Отмена</button>
      </div>
    </div>
  );
};
