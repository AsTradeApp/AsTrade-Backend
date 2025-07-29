// 🎁 Ejemplo de uso en React Native Frontend

// 1. OBTENER DATOS DE RECOMPENSAS
const fetchDailyRewards = async (userId) => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/rewards/daily-status', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-User-ID': userId
      }
    });
    
    const data = await response.json();
    return data.data.week_rewards;
  } catch (error) {
    console.error('Error fetching rewards:', error);
    return [];
  }
};

// 2. COMPONENTE DE RECOMPENSA
const RewardCard = ({ reward, isClaimed, isLocked }) => {
  const { day, amount, type, image_url } = reward;
  
  // Construir URL completa de la imagen
  const fullImageUrl = image_url 
    ? `http://localhost:8000${image_url}`  // Para desarrollo
    : null;
  
  return (
    <View style={styles.rewardCard}>
      <Text style={styles.dayText}>Día {day}</Text>
      
      {/* Mostrar imagen si existe */}
      {fullImageUrl && (
        <Image 
          source={{ uri: fullImageUrl }}
          style={styles.rewardImage}
          resizeMode="contain"
        />
      )}
      
      <Text style={styles.amountText}>{amount} créditos</Text>
      <Text style={styles.typeText}>{type}</Text>
      
      {isClaimed && <Text style={styles.claimedText}>✅ Reclamado</Text>}
      {isLocked && <Text style={styles.lockedText}>🔒 Bloqueado</Text>}
    </View>
  );
};

// 3. COMPONENTE PRINCIPAL
const DailyRewardsScreen = () => {
  const [rewards, setRewards] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadRewards();
  }, []);
  
  const loadRewards = async () => {
    const userId = 'fb16ec78-ff70-4895-9ace-92a1d8202fdb'; // Tu user ID
    const rewardsData = await fetchDailyRewards(userId);
    setRewards(rewardsData);
    setLoading(false);
  };
  
  if (loading) {
    return <Text>Cargando recompensas...</Text>;
  }
  
  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>🎁 Recompensas Diarias</Text>
      
      {rewards.map((rewardData, index) => (
        <RewardCard 
          key={index}
          reward={rewardData.reward}
          isClaimed={rewardData.is_claimed}
          isLocked={rewardData.is_locked}
        />
      ))}
    </ScrollView>
  );
};

// 4. ESTILOS
const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20
  },
  rewardCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3
  },
  dayText: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8
  },
  rewardImage: {
    width: 100,
    height: 100,
    alignSelf: 'center',
    marginVertical: 8
  },
  amountText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#007AFF'
  },
  typeText: {
    fontSize: 14,
    color: '#666',
    marginTop: 4
  },
  claimedText: {
    color: 'green',
    fontWeight: 'bold',
    marginTop: 8
  },
  lockedText: {
    color: 'orange',
    fontWeight: 'bold',
    marginTop: 8
  }
});

export default DailyRewardsScreen; 