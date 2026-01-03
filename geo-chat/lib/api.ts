// API utility functions for backend communication using the universal framework API

// Next.js replaces NEXT_PUBLIC_* env vars at build time
// In Next.js, these are available both server and client side
declare const process: {
  env: {
    [key: string]: string | undefined;
  };
} | undefined;

const getEnv = (key: string, defaultValue: string): string => {
  if (typeof process !== 'undefined' && process?.env?.[key]) {
    return process.env[key]!;
  }
  return defaultValue;
};

// Universal framework API (uses geo-chat framework)
const UNIVERSAL_API_URL = getEnv('NEXT_PUBLIC_UNIVERSAL_API_URL', 'http://localhost:8000');

// Legacy API URLs (for traffic and bikes until they're added to framework)
const TRAFFIC_API_URL = getEnv('NEXT_PUBLIC_TRAFFIC_API_URL', 'http://localhost:8002');
const BIKES_API_URL = getEnv('NEXT_PUBLIC_BIKES_API_URL', 'http://localhost:8003');

// Framework DataPoint format (from geo_chat.core.models)
export interface DataPoint {
  category: string;
  source: string;
  location: {
    lat: number;
    lon: number;
    name?: string;
    city?: string;
    province?: string;
    country?: string;
    address?: string;
  };
  timestamp: string;
  metrics: {
    [key: string]: any;
  };
  metadata?: {
    [key: string]: any;
  };
  raw?: {
    [key: string]: any;
  };
  error?: string;
}

// Compatible interfaces for existing code
export interface EnvironmentData extends DataPoint {
  metrics: {
    temperature?: number;
    humidity?: number;
    pressure?: number;
    rain_1h?: number;
    snow_1h?: number;
    pm25?: number;
    pm10?: number;
    aqi?: number;
  };
}

export interface DoctorData {
  provider: string;
  place: string;
  address: string;
  locality: string;
  phone: string;
  service: string;
  waiting_days: number;
  awaiting: number;
  queue_date: string;
  date_updated?: string;
  lat?: number;
  lon?: number;
}

export interface DoctorsResponse {
  query: {
    service: string;
    urgent: boolean;
    lat: number;
    lon: number;
    city: string;
    province: string;
    province_code: string;
    timestamp: string;
  };
  results: DoctorData[];
  data_point?: DataPoint; // Full framework response
}

export interface TrafficData {
  category: string;
  source: string;
  location: {
    lat: number;
    lon: number;
    name?: string;
  };
  timestamp: string;
  metrics: {
    current_speed?: number;
    free_flow_speed?: number;
    confidence?: number;
    location_name?: string;
  };
}

export interface BikeData {
  name: string;
  city: string;
  lat: number;
  lon: number;
  bikes_available: number;
  docks_available: number;
  system_brand: string;
  rental_key?: string;
  spot_id?: string;
}

// Universal Framework API - Weather Provider
export async function fetchEnvironmentData(
  lat: number,
  lon: number,
  name?: string
): Promise<EnvironmentData> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
  });
  if (name) {
    params.append('name', name);
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
  
  try {
    const response = await fetch(`${UNIVERSAL_API_URL}/providers/weather?${params}`, {
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      // Don't throw for missing API key or server errors - return null instead
      const errorData = await response.json().catch(() => ({}));
      if (errorData.error?.includes('API key')) {
        console.warn('Weather API key not configured. Weather data will not be available.');
        return null as any; // Return null for optional service
      }
      throw new Error(`Failed to fetch environment data: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // Handle error in response
    if (data.error) {
      if (data.error.includes('API key')) {
        console.warn('Weather API key not configured. Weather data will not be available.');
        return null as any; // Return null for optional service
      }
      throw new Error(data.error);
    }
    
    return data as EnvironmentData;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Timeout: Backend nie odpowiada. Upewnij się, że serwer działa na http://localhost:8000');
    }
    // For network errors, return null instead of throwing (optional service)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      console.warn('Weather service unavailable:', error.message);
      return null as any;
    }
    throw error;
  }
}

export async function fetchEnvironmentBatch(
  points: Array<{ lat: number; lon: number; name?: string }>
): Promise<EnvironmentData[]> {
  const response = await fetch(`${UNIVERSAL_API_URL}/providers/weather/batch`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(points),
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch environment batch: ${response.statusText}`);
  }
  const result = await response.json();
  return result.results as EnvironmentData[];
}

// Universal Framework API - Doctors Provider
export async function fetchDoctorsData(
  lat: number,
  lon: number,
  serviceName: string,
  urgent: boolean = false
): Promise<DoctorsResponse> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
    service_name: serviceName,
    urgent: urgent.toString(),
  });

  const response = await fetch(`${UNIVERSAL_API_URL}/providers/doctors?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch doctors data: ${response.statusText}`);
  }
  const data = await response.json();
  
  if (data.error) {
    throw new Error(data.error);
  }
  
  return data as DoctorsResponse;
}

export async function fetchDoctorsCoordinates(
  lat: number,
  lon: number,
  serviceName: string,
  urgent: boolean = false
): Promise<DoctorsResponse> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
    service_name: serviceName,
    urgent: urgent.toString(),
  });

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);
  
  try {
    const response = await fetch(`${UNIVERSAL_API_URL}/providers/doctors/coordinates?${params}`, {
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch doctors coordinates: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }
    
    return data as DoctorsResponse;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Timeout: Backend nie odpowiada. Upewnij się, że serwer działa na http://localhost:8000');
    }
    throw error;
  }
}

// Generic Framework API - Any Provider
export async function fetchProviderData(
  providerName: string,
  lat: number,
  lon: number,
  name?: string,
  options?: { [key: string]: any }
): Promise<DataPoint> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
  });
  if (name) {
    params.append('name', name);
  }
  if (options) {
    Object.entries(options).forEach(([key, value]) => {
      params.append(key, value.toString());
    });
  }

  const response = await fetch(`${UNIVERSAL_API_URL}/providers/${providerName}?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${providerName} data: ${response.statusText}`);
  }
  const data = await response.json();
  
  if (data.error) {
    throw new Error(data.error);
  }
  
  return data as DataPoint;
}

// Legacy APIs (until traffic and bikes are added to framework)
export async function fetchTrafficData(
  lat: number,
  lon: number,
  name?: string
): Promise<TrafficData | null> {
  const params = new URLSearchParams({
    lat: lat.toString(),
    lon: lon.toString(),
  });
  if (name) {
    params.append('name', name);
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
    
    const response = await fetch(`${TRAFFIC_API_URL}/traffic?${params}`, {
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      console.warn('Traffic service unavailable:', response.statusText);
      return null; // Return null for optional service
    }
    
    const data = await response.json();
    
    if (data.error) {
      console.warn('Traffic service error:', data.error);
      return null; // Return null for optional service
    }
    
    return data as TrafficData;
  } catch (error) {
    // Network errors or timeouts - return null instead of throwing
    console.warn('Traffic service unavailable:', error instanceof Error ? error.message : 'Unknown error');
    return null;
  }
}

export async function fetchTrafficBatch(
  points: Array<{ lat: number; lon: number; name?: string }>
): Promise<TrafficData[]> {
  const response = await fetch(`${TRAFFIC_API_URL}/traffic/batch`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(points),
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch traffic batch: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchBikesData(): Promise<BikeData[] | null> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
    
    const response = await fetch(`${BIKES_API_URL}/nextbike`, {
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      console.warn('Bikes service unavailable:', response.statusText);
      return null; // Return null for optional service
    }
    
    const data = await response.json();
    
    if (data.error) {
      console.warn('Bikes service error:', data.error);
      return null; // Return null for optional service
    }
    
    return data as BikeData[];
  } catch (error) {
    // Network errors or timeouts - return null instead of throwing
    console.warn('Bikes service unavailable:', error instanceof Error ? error.message : 'Unknown error');
    return null;
  }
}
