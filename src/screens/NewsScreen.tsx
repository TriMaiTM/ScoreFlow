import React, { useState } from 'react';
import { View, StyleSheet, FlatList, TouchableOpacity, Image, Linking, RefreshControl, StatusBar, ScrollView, Platform, useWindowDimensions } from 'react-native';
import { Text, Surface, ActivityIndicator, IconButton } from 'react-native-paper';
import { useQuery } from '@tanstack/react-query';
import { LinearGradient } from 'expo-linear-gradient';
import { useNavigation } from '@react-navigation/native';
import { NewsService, NewsItem } from '../services/NewsService';
import { formatDistanceToNow } from 'date-fns';
import { vi } from 'date-fns/locale';

export default function NewsScreen() {
    const navigation = useNavigation();
    const { width } = useWindowDimensions();

    const { data: newsResponse, isLoading, refetch, isError } = useQuery({
        queryKey: ['news'],
        queryFn: () => NewsService.getNews(0, 20),
    });

    const newsData = Array.isArray(newsResponse) ? newsResponse : (newsResponse?.data || []);
    const featuredNews = newsData.slice(0, 3);
    const otherNews = newsData.slice(3);

    const handleOpenLink = (url: string) => {
        Linking.openURL(url).catch(err => console.error("Couldn't load page", err));
    };

    const formatTime = (dateString: string) => {
        try {
            return formatDistanceToNow(new Date(dateString), { addSuffix: true, locale: vi });
        } catch (e) {
            return 'Vừa xong';
        }
    };

    const renderFeaturedItem = ({ item }: { item: NewsItem }) => (
        <TouchableOpacity
            activeOpacity={0.9}
            onPress={() => handleOpenLink(item.url)}
            style={[styles.featuredItem, { width: width }]} // Dynamic width
        >
            <Image
                source={{ uri: item.imageUrl || 'https://via.placeholder.com/400x200?text=News' }}
                style={styles.featuredImage}
                resizeMode="cover"
            />
            <LinearGradient
                colors={['transparent', 'rgba(0,0,0,0.6)', 'rgba(0,0,0,0.9)']}
                style={styles.featuredGradient}
            >
                <View style={styles.sourceTag}>
                    <Text style={styles.featuredSource}>{item.source}</Text>
                    <Text style={styles.featuredTime}>• {formatTime(item.publishedAt)}</Text>
                </View>
                <Text style={styles.featuredTitle} numberOfLines={2}>{item.title}</Text>
            </LinearGradient>
        </TouchableOpacity>
    );

    const RenderListItem = ({ item }: { item: NewsItem }) => (
        <TouchableOpacity
            activeOpacity={0.7}
            onPress={() => handleOpenLink(item.url)}
            style={styles.listItem}
        >
            <View style={styles.listItemContent}>
                <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 6 }}>
                    <Text style={styles.listSource}>{item.source}</Text>
                    <Text style={styles.listTime}> • {formatTime(item.publishedAt)}</Text>
                </View>
                <Text style={styles.listTitle} numberOfLines={3}>{item.title}</Text>
            </View>
            {item.imageUrl && (
                <Image
                    source={{ uri: item.imageUrl }}
                    style={styles.listImage}
                    resizeMode="cover"
                />
            )}
        </TouchableOpacity>
    );

    return (
        <View style={styles.container}>
            <StatusBar barStyle="light-content" backgroundColor="#0F172A" />

            {/* Header */}
            <View style={styles.header}>
                <Text style={styles.headerTitle}>Tin mới nhất</Text>
                {/* Manual Refresh Button in Header if needed */}
                <IconButton icon="refresh" iconColor="#fff" size={20} onPress={() => refetch()} />
            </View>

            {isLoading ? (
                <View style={styles.centerContainer}>
                    <ActivityIndicator size="large" color="#3B82F6" />
                </View>
            ) : isError ? (
                <View style={styles.centerContainer}>
                    <Text style={{ color: '#EF4444', marginBottom: 10 }}>Không tải được tin tức</Text>
                    <IconButton icon="refresh" iconColor="#fff" onPress={() => refetch()} />
                </View>
            ) : (
                <ScrollView
                    refreshControl={
                        <RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor="#fff" />
                    }
                    contentContainerStyle={{ paddingBottom: 20 }}
                >
                    {/* Featured Carousel */}
                    {featuredNews.length > 0 && (
                        <View style={styles.carouselContainer}>
                            <FlatList
                                data={featuredNews}
                                renderItem={renderFeaturedItem}
                                horizontal
                                pagingEnabled
                                showsHorizontalScrollIndicator={false}
                                keyExtractor={item => `featured-${item.id}`}
                                snapToInterval={width} // Ensure locking to item width
                                decelerationRate="fast"
                            />
                        </View>
                    )}

                    {/* List Section */}
                    <View style={styles.listContainer}>
                        {otherNews.map(item => (
                            <RenderListItem key={item.id} item={item} />
                        ))}
                        {newsData.length === 0 && (
                            <Text style={{ color: '#94A3B8', textAlign: 'center', marginTop: 20 }}>
                                Chưa có tin tức nào.
                            </Text>
                        )}
                    </View>

                </ScrollView>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#0F172A',
    },
    header: {
        paddingTop: Platform.OS === 'android' ? 40 : 60,
        paddingBottom: 12,
        paddingHorizontal: 20,
        backgroundColor: '#0F172A',
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderBottomWidth: 1,
        borderBottomColor: 'rgba(255,255,255,0.05)',
    },
    headerTitle: {
        color: '#fff',
        fontSize: 22,
        fontWeight: 'bold',
    },
    centerContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    carouselContainer: {
        height: 240, // Increased height slightly
        marginBottom: 20,
    },
    featuredItem: {
        height: 240,
        position: 'relative',
    },
    featuredImage: {
        width: '100%',
        height: '100%',
    },
    featuredGradient: {
        position: 'absolute',
        left: 0,
        right: 0,
        bottom: 0,
        height: '70%', // Higher gradient for better text readability
        justifyContent: 'flex-end',
        padding: 20,
    },
    sourceTag: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 8,
    },
    featuredSource: {
        color: '#3B82F6',
        fontSize: 12,
        fontWeight: 'bold',
        textTransform: 'uppercase',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        paddingHorizontal: 6,
        paddingVertical: 2,
        borderRadius: 4,
        overflow: 'hidden',
    },
    featuredTime: {
        color: '#cbd5e1', // Light gray
        fontSize: 12,
        marginLeft: 6,
    },
    featuredTitle: {
        color: '#fff',
        fontSize: 18,
        fontWeight: 'bold',
        lineHeight: 26,
        textShadowColor: 'rgba(0, 0, 0, 0.75)',
        textShadowOffset: { width: 0, height: 1 },
        textShadowRadius: 3,
    },
    listContainer: {
        paddingHorizontal: 20,
    },
    listItem: {
        flexDirection: 'row',
        marginBottom: 16,
        backgroundColor: '#1E293B',
        borderRadius: 12,
        overflow: 'hidden',
        padding: 12,
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.05)',
    },
    listItemContent: {
        flex: 1,
        paddingRight: 12,
        justifyContent: 'space-between',
    },
    listSource: {
        color: '#3B82F6',
        fontSize: 11,
        fontWeight: '700',
        textTransform: 'uppercase',
    },
    listTime: {
        color: '#64748B',
        fontSize: 11,
    },
    listTitle: {
        color: '#f1f5f9',
        fontSize: 14,
        fontWeight: '600',
        lineHeight: 20,
    },
    listSummary: {
        color: '#94A3B8',
        fontSize: 12,
        marginTop: 4,
    },
    listImage: {
        width: 90,
        height: 90,
        borderRadius: 8,
        backgroundColor: '#334155',
    },
});
