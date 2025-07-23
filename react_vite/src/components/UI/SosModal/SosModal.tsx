import { useSendSosMutation } from "../../../features/messanger/MessageApi";
import type { SosType } from "../Content/types";
import styled from "./SosModal.module.css";

export const SosModal: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const [sendSosApi, { isLoading }] = useSendSosMutation();

  const sendSOS = async (typeSos: SosType) => {
    if (!navigator.geolocation) {
      alert("Геолокация не поддерживается браузером.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;

        const payload = {
          type: typeSos,
          latitude: latitude,
          longitude: longitude,
        };

        try {
          await sendSosApi(payload).unwrap(); // запрос к RTK Query API

          onClose(); // Закрыть модалку после успешного SOS
        } catch (err) {
          alert(`Ошибка при отправке SOS. ${err}`);
        }
      },
      () => {
        alert("Не удалось определить местоположение.");
      }
    );
  };

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className={styled.modalOverlay} onClick={handleOverlayClick}>
      <div className={styled.modal}>
        <h2>Выберите ситуацию</h2>
        <button disabled={isLoading} onClick={() => sendSOS("dtp")}>
          Попал в ДТП
        </button>
        <button disabled={isLoading} onClick={() => sendSOS("conflict")}>
          Конфликтная ситуация
        </button>
        <button onClick={onClose}>Отмена</button>
      </div>
    </div>
  );
};
