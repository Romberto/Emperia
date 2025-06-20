import { type TypedUseSelectorHook, useSelector } from "react-redux";
import type { RootState } from "../app/store";

// useSelector с типами из RootState
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;