import { useState } from 'react';
import axios from 'axios';

function App() {
  const [email, setEmail] = useState('test@test.ru');
  const [password, setPassword] = useState('password123');
  const [token, setToken] = useState('');
  const [sport, setSport] = useState('run');
  const [duration, setDuration] = useState(60);
  const [sessions, setSessions] = useState(3);
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState('');

  // URL твоего бэкенда
  const API_URL = 'http://localhost:8000/api/v1';

  const handleLogin = async () => {
    try {
      setError('');
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      
      const res = await axios.post(`${API_URL}/auth/login`, formData);
      setToken(res.data.access_token);
    } catch (err) {
      setError('Ошибка входа. Проверьте логин и пароль.');
    }
  };

  const handleBuildPlan = async () => {
    try {
      setError('');
      const res = await axios.post(`${API_URL}/plan/`, 
        { sport, duration_min: Number(duration), sessions_per_week: Number(sessions) },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setPlan(res.data);
    } catch (err) {
      if (err.response?.status === 503) {
        setError('Сервис погоды временно недоступен. Попробуйте позже.');
      } else {
        setError('Ошибка при построении плана.');
      }
    }
  };

  return (
    <div className="container">
      <h1>WeatherFit 🏃‍♂️</h1>
      
      {!token ? (
        <div>
          <h3>Вход в систему</h3>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" />
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Пароль" />
          <button onClick={handleLogin}>Войти</button>
        </div>
      ) : (
        <div>
          <h3>Построить план</h3>
          <select value={sport} onChange={e => setSport(e.target.value)}>
            <option value="run">Бег</option>
            <option value="bike">Велосипед</option>
            <option value="workout">Воркаут</option>
          </select>
          <input type="number" value={duration} onChange={e => setDuration(e.target.value)} placeholder="Длительность (мин)" />
          <input type="number" value={sessions} onChange={e => setSessions(e.target.value)} placeholder="Раз в неделю" />
          <button onClick={handleBuildPlan}>Построить план</button>
          <button onClick={() => setToken('')} style={{backgroundColor: '#e74c3c', marginTop: '5px'}}>Выйти</button>
        </div>
      )}

      {error && <p style={{color: 'red'}}>{error}</p>}

      {plan && (
        <div className="result">
          <h3>Ваш план готов!</h3>
          <p>Статус: {plan.degraded ? 'Деградация (неполные данные)' : 'Успешно'}</p>
          <pre>{JSON.stringify(plan.payload.windows, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
