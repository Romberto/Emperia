import { useDispatch } from "react-redux";
import type { AppDispatch } from "../app/store"; // путь зависит от твоей структуры

export const useAppDispatch = () => useDispatch<AppDispatch>();