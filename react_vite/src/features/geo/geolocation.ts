type Coordinates = {
  latitude: number;
  longitude: number;
};

type LocationInfo = {
  city?: string;
  country?: string;
  error?: string;
};

export async function getCityFromLocation(): Promise<LocationInfo> {
  // Получение координат
  const getPosition = (): Promise<Coordinates> =>
    new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error("Geolocation is not supported by this browser."));
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
        },
        (error) => {
          reject(new Error("Unable to retrieve location: " + error.message));
        }
      );
    });

  try {
    const { latitude, longitude } = await getPosition();

    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`
    );

    const data = await response.json();

    return {
      city: data.address.city || data.address.town || data.address.village,
      country: data.address.country,
    };
  } catch (error: any) {
    return { error: error.message };
  }
}


