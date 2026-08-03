import { getAccessToken, httpClient, onUnauthorized, setAccessToken } from './httpClient';

describe('httpClient', () => {
  afterEach(() => {
    setAccessToken(null);
  });

  it('stores and returns the current access token', () => {
    expect(getAccessToken()).toBeNull();
    setAccessToken('token-123');
    expect(getAccessToken()).toBe('token-123');
  });

  it('attaches the bearer token to outgoing request config once set', async () => {
    setAccessToken('token-123');
    const requestInterceptor = (httpClient.interceptors.request as any).handlers[0].fulfilled;
    const config = await requestInterceptor({ headers: createAxiosHeaders() });
    expect(config.headers.get('Authorization')).toBe('Bearer token-123');
  });

  it('does not attach a header when no token has been set', async () => {
    const requestInterceptor = (httpClient.interceptors.request as any).handlers[0].fulfilled;
    const config = await requestInterceptor({ headers: createAxiosHeaders() });
    expect(config.headers.get('Authorization')).toBeUndefined();
  });

  it('clears the token and notifies the registered handler on a 401 response', async () => {
    setAccessToken('token-123');
    const handler = jest.fn();
    onUnauthorized(handler);
    const responseInterceptor = (httpClient.interceptors.response as any).handlers[0].rejected;

    await expect(responseInterceptor({ response: { status: 401 } })).rejects.toBeDefined();

    expect(getAccessToken()).toBeNull();
    expect(handler).toHaveBeenCalledTimes(1);
  });

  it('leaves the session untouched on non-401 errors', async () => {
    setAccessToken('token-123');
    const handler = jest.fn();
    onUnauthorized(handler);
    const responseInterceptor = (httpClient.interceptors.response as any).handlers[0].rejected;

    await expect(responseInterceptor({ response: { status: 500 } })).rejects.toBeDefined();

    expect(getAccessToken()).toBe('token-123');
    expect(handler).not.toHaveBeenCalled();
  });
});

// axios' real AxiosHeaders class supports .set()/.get(); a plain object is not
// enough for the interceptor under test, so build a minimal stand-in here.
function createAxiosHeaders(): { set: (k: string, v: string) => void; get: (k: string) => string | undefined } {
  const store = new Map<string, string>();
  return {
    set: (k, v) => store.set(k, v),
    get: (k) => store.get(k),
  };
}
