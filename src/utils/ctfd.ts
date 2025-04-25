import config from "../config/config.ts";
import axios, { AxiosInstance } from "axios";
import axiosRetry from "axios-retry";
import NodeCache from "node-cache";
import { logger } from "../utils/logger.ts";

interface CTFChallenge {
    id: number;
    name: string;
    value: number;
    type: string;
    category: string;
    solves: number;
}

const CACHE_TTL = 30; // seconds

// in-memory cache
const cache = new NodeCache({ stdTTL: CACHE_TTL, checkperiod: CACHE_TTL / 2 });

function createApiClient(): AxiosInstance {
    const client = axios.create({
        baseURL: `${config.CTFD_URL}/api/v1`,
        headers: {
            Authorization: `Token ${config.CTFD_API_TOKEN}`,
            "Content-Type": "application/json",
        },
        timeout: 5_000,
    });

    // Retry on network errors / 5xx / 429
    axiosRetry(client, {
        retries: 3,
        retryDelay: axiosRetry.exponentialDelay,
        retryCondition: axiosRetry.isRetryableError,
    });

    return client;
}

const api = createApiClient();

async function fetchFromApi<T>(key: string, endpoint: string): Promise<T> {
    const cached = cache.get<T>(key);
    if (cached) {
        return cached;
    }

    try {
        const { data } = await api.get<{ data: T }>(endpoint);
        cache.set(key, data.data);
        return data.data;
    } catch (error) {
        logger(`Error fetching ${endpoint}`, "error");
        throw new Error("Could not reach CTFd API. Please try again later.");
    }
}

/** Return all challenges */
export function getChallenges(): Promise<CTFChallenge[]> {
    return fetchFromApi<CTFChallenge[]>("challenges", "/challenges");
}
