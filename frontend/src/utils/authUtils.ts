// Auth utility functions for consistent session management

export const isAuthenticated = (): boolean => {
    return localStorage.getItem('signedIn') === 'true' && !!localStorage.getItem('auth_token');
};

export const getUserEmail = (): string => {
    return localStorage.getItem('user_email') || '';
};

export const getAuthToken = (): string | null => {
    return localStorage.getItem('auth_token');
};

export const setAuth = (email: string, token?: string): void => {
    localStorage.setItem('signedIn', 'true');
    localStorage.setItem('user_email', email);
    if (token) {
        localStorage.setItem('auth_token', token);
    }
};

export const clearAuth = (): void => {
    localStorage.removeItem('signedIn');
    localStorage.removeItem('user_email');
    localStorage.removeItem('auth_token');
};

// Helper to get Authorization header for API requests
export const getAuthHeaders = (): Record<string, string> => {
    const token = getAuthToken();
    if (token) {
        return { 'Authorization': `Bearer ${token}` };
    }
    return {};
};
