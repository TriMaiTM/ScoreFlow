import { apiClient } from './ApiClient';

export interface NewsItem {
    id: number;
    title: string;
    summary: string;
    url: string;
    imageUrl: string | null;
    source: string;
    publishedAt: string;
    timeAgo: string;
}

export class NewsService {
    static async getNews(skip = 0, limit = 20) {
        console.log(`📡 NewsService: Calling API /news?skip=${skip}&limit=${limit}`);
        const response = await apiClient.get<NewsItem[]>(`/news?skip=${skip}&limit=${limit}`);
        console.log("📡 NewsService: Response received:", response);
        return response;
    }
}
