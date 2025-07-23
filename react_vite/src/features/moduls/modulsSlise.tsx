import { createSlice } from "@reduxjs/toolkit";
interface ModulsState {
  sosModulIsOpen: boolean;
}

const initialState: ModulsState = {
  sosModulIsOpen: false,
};

export const ModulSlice = createSlice({
  name: "modul",
  initialState,
  reducers: {
    setSosModulOpen: (state) => {
      state.sosModulIsOpen = true;
    },
    setSosModulClose: (state) => {
      state.sosModulIsOpen = false;
    },
  },
});
export const { setSosModulOpen, setSosModulClose } = ModulSlice.actions;
export default ModulSlice.reducer;
