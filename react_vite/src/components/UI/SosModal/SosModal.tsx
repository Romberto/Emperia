import { useSendSosMutation } from "../../../features/messanger/MessageApi";
import { Button } from "../Button/Button";
import type { SosType } from "../Content/types";
import styled from "./SosModal.module.css";

export const SosModal: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const [sendSosApi, { isLoading }] = useSendSosMutation();

  const sendSOS = async (typeSos: SosType) => {
    if (!navigator.geolocation) {
      alert("Геолокация не поддерживается этим браузером.");
      onClose();
      return;
    }

    // Проверка разрешения, если API доступен
    try {
      const permission = await navigator.permissions?.query?.({
        name: "geolocation" as PermissionName,
      });

      if (permission?.state === "denied") {
        alert("Геолокация отключена. Проверьте настройки Safari или браузера.");
        onClose();
        return;
      }
    } catch (e) {
      console.warn("Не удалось проверить разрешения на геолокацию", e);
      // Safari может не поддерживать Permissions API, пропускаем проверку
    }

    // Запрос координат
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;

        const payload = {
          type: typeSos,
          latitude,
          longitude,
        };

        try {
          await sendSosApi(payload).unwrap(); // RTK Query API вызов
          onClose(); // Закрыть модалку после успеха
        } catch (err: any) {
          alert(
            `Ошибка при отправке SOS: ${
              err.data?.detail || err.error || JSON.stringify(err)
            }`
          );
          onClose();
        }
      },
      (error) => {
        alert(
          `Не удалось определить местоположение: ${
            error.message || "Неизвестная ошибка"
          }`
        );
        onClose();
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
        {!isLoading ? (
          <div className={styled.modal_view}>
            <h2>Выберите ситуацию</h2>
            <Button
              style={{ fontSize: 25, width: "90%" }}
              disabled={isLoading}
              onClick={() => sendSOS("dtp")}
            >
              Попал в ДТП
            </Button>
            <Button
              style={{ fontSize: 25, width: "90%" }}
              disabled={isLoading}
              onClick={() => sendSOS("conflict")}
            >
              Конфликтная ситуация
            </Button>
          </div>
        ) : (
          <div className={styled.spiner_base}>
            <p>отправляю сообщение</p>
            <div className={styled.spiner}></div>
          </div>
        )}
      </div>
    </div>
  );
};
