const roomPalettes = [
  "linear-gradient(135deg, #0f766e 0%, #115e59 100%)",
  "linear-gradient(135deg, #365f73 0%, #294858 100%)",
  "linear-gradient(135deg, #3f6b57 0%, #315444 100%)",
  "linear-gradient(135deg, #59677f 0%, #414d64 100%)",
  "linear-gradient(135deg, #7a5c48 0%, #604535 100%)",
];

export const roomPalette = (id: string | number) => {
  const value = String(id).split("").reduce((sum, char) => sum + char.charCodeAt(0), 0);
  return roomPalettes[value % roomPalettes.length];
};
