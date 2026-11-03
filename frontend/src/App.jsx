import { useState } from 'react';
import axios from 'axios';
import './index.css';

const API_URL = 'http://localhost:8000/api/v1';

export default function App() {
  // Состояния навигации
  const [view, setView] = useState('home'); // 'home', 'login', 'register', 'dashboard'
  const [token, setToken] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Данные пользователя для регистрации
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [city, setCity] = useState('Санкт-Петербург');
  const [lat, setLat] = useState(59.93);
  const [lon, setLon] = useState(30.33);

  // Данные для плана
  const [sport, setSport] = useState('run');
  const [duration, setDuration] = useState(60);
  const [sessions, setSessions] = useState(3);
  const [plan, setPlan] = useState(null);

  // --- ЛОГИКА ---
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      setError('');
      setLoading(true);
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      const res = await axios.post(`${API_URL}/auth/login`, formData);
      setToken(res.data.access_token);
      setView('dashboard');
    } catch (err) {
      setError('Неверный email или пароль');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      setError('');
      setLoading(true);
      const res = await axios.post(`${API_URL}/auth/register`, {
        email, password, city, lat: Number(lat), lon: Number(lon)
      });
      setToken(res.data.access_token);
      setView('dashboard');
    } catch (err) {
      setError('Ошибка регистрации. Возможно, такой email уже существует.');
    } finally {
      setLoading(false);
    }
  };

  const handleBuildPlan = async () => {
    try {
      setError('');
      setPlan(null);
      setLoading(true);
      const res = await axios.post(`${API_URL}/plan/`, 
        { sport, duration_min: Number(duration), sessions_per_week: Number(sessions) },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setPlan(res.data);
    } catch (err) {
      if (err.response?.status === 503) {
        setError('Сервис погоды временно недоступен (Open-Meteo не отвечает). Попробуйте позже.');
      } else if (err.response?.status === 401) {
        setError('Сессия истекла. Войдите заново.');
        setView('login');
        setToken('');
      } else {
        setError('Ошибка при построении плана. Попробуйте еще раз.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken('');
    setView('home');
    setPlan(null);
  };

  // --- ОТРИСОВКА СТРАНИЦ ---

  // 1. Главная страница
  const renderHome = () => (
    <div className="hero-section">
      <h1 className="hero-title">Идеальная погода для ваших тренировок</h1>
      <p className="hero-subtitle">
        Мы анализируем прогноз погоды, качество воздуха и УФ-индекс, чтобы составить для вас идеальный план уличных тренировок на неделю.
      </p>
      <div className="hero-buttons">
        <button className="btn-primary btn-large" onClick={() => setView('register')}>Начать бесплатно</button>
        <button className="btn-outline btn-large" onClick={() => setView('login')}>Войти в аккаунт</button>
      </div>
      <div className="features">
        <div className="feature-card">
          <span className="feature-icon">🏃‍♂️</span>
          <h3>Умный подбор</h3>
          <p>Учитываем температуру, ветер, дождь и даже смог.</p>
        </div>
        <div className="feature-card">
          <span className="feature-icon">📅</span>
          <h3>План на неделю</h3>
          <p>Получите готовое расписание с лучшими часами для спорта.</p>
        </div>
        <div className="feature-card">
          <span className="feature-icon">🔔</span>
          <h3>Уведомления</h3>
          <p>Напомним за 2 часа до идеального окна для тренировки.</p>
        </div>
      </div>
    </div>
  );

  // 2. Форма входа
  const renderLogin = () => (
    <div className="auth-container">
      <div className="auth-card">
        <h2>С возвращением!</h2>
        <p className="auth-subtitle">Войдите, чтобы увидеть свой план</p>
        {error && <div className="error-msg">{error}</div>}
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Пароль</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>
          <button type="submit" className="btn-primary w-100" disabled={loading}>
            {loading ? 'Вход...' : 'Войти'}
          </button>
        </form>
        <p className="auth-switch">Нет аккаунта? <span onClick={() => { setView('register'); setError(''); }}>Зарегистрироваться</span></p>
      </div>
    </div>
  );

  // 3. Форма регистрации
  const renderRegister = () => (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Создать аккаунт</h2>
        <p className="auth-subtitle">Присоединяйтесь к WeatherFit</p>
        {error && <div className="error-msg">{error}</div>}
        <form onSubmit={handleRegister}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Пароль</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength="6" />
          </div>
          <div className="form-group">
            <label>Город</label>
            <select value={city} onChange={e => {
              setCity(e.target.value);
              // Простая логика координат для городов
              if (e.target.value === 'Москва') { setLat(55.75); setLon(37.61); }
              if (e.target.value === 'Санкт-Петербург') { setLat(59.93); setLon(30.33); }
              if (e.target.value === 'Казань') { setLat(55.79); setLon(49.12); }
            }}>
              <option value="Санкт-Петербург">Санкт-Петербург</option>
              <option value="Москва">Москва</option>
              <option value="Казань">Казань</option>
            </select>
          </div>
          <button type="submit" className="btn-primary w-100" disabled={loading}>
            {loading ? 'Создание...' : 'Зарегистрироваться'}
          </button>
        </form>
        <p className="auth-switch">Уже есть аккаунт? <span onClick={() => { setView('login'); setError(''); }}>Войти</span></p>
      </div>
    </div>
  );

  // 4. Личный кабинет (Дашборд)
  const renderDashboard = () => (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>Личный кабинет</h2>
        <button className="btn-outline" onClick={handleLogout}>Выйти</button>
      </div>
      
      {error && <div className="error-msg">{error}</div>}

      <div className="dashboard-grid">
        <div className="dashboard-form card">
          <h3>Параметры тренировки</h3>
          <div className="form-group">
            <label>Вид спорта</label>
            <select value={sport} onChange={e => setSport(e.target.value)}>
              <option value="run">Бег</option>
              <option value="bike">Велосипед</option>
              <option value="workout">Воркаут</option>
            </select>
          </div>
          <div className="form-group">
            <label>Длительность (мин)</label>
            <input type="number" value={duration} onChange={e => setDuration(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Тренировок в неделю</label>
            <input type="number" value={sessions} onChange={e => setSessions(e.target.value)} />
          </div>
          <button className="btn-primary w-100" onClick={handleBuildPlan} disabled={loading}>
            {loading ? 'Анализируем погоду...' : 'Построить план'}
          </button>
        </div>

        <div className="dashboard-results card">
          <h3>Ваш план</h3>
          {!plan ? (
            <p className="empty-state">Нажмите «Построить план», чтобы увидеть лучшие окна для тренировок.</p>
          ) : (
            <div>
              {plan.degraded && <p className="warning">⚠️ Качество воздуха недоступно.</p>}
              <div className="windows-list">
                {plan.payload.windows.map((w, index) => (
                  <div key={index} className="window-card">
                    <div>
                      <div className="window-date">{new Date(w.start).toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' })}</div>
                      <div className="window-time">{new Date(w.start).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })} — {new Date(w.end).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}</div>
                    </div>
                    <div className="window-score">{w.avg_score} / 100</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // Главный рендер с шапкой
  return (
    <div className="app-wrapper">
      <header className="main-header">
        <div className="logo" onClick={() => setView('home')}>
          🏃‍♂️ WeatherFit
        </div>
        <nav className="nav-links">
          {view === 'home' && (
            <>
              <button className="nav-btn" onClick={() => setView('login')}>Войти</button>
              <button className="nav-btn btn-primary" onClick={() => setView('register')}>Регистрация</button>
            </>
          )}
        </nav>
      </header>

      <main className="main-content">
        {view === 'home' && renderHome()}
        {view === 'login' && renderLogin()}
        {view === 'register' && renderRegister()}
        {view === 'dashboard' && renderDashboard()}
      </main>
    </div>
  );
}