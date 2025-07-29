from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID
import json
from supabase import create_client, Client
from app.config.settings import settings
from app.models.rewards import (
    DailyReward, RewardConfig, UserStreak, 
    DailyRewardResponse, ClaimRewardResponse
)

class RewardsService:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.supabase_url, 
            settings.supabase_key
        )
        
        # Configuración de recompensas (se cargará desde la base de datos)
        self.default_daily_rewards = []
        self.galaxy_explorer_reward = {
            "amount": 25, 
            "currency": "credits", 
            "type": "galaxy_credits",
            "description": "Galaxy Explorer Bonus"
        }
        
        # Configuración de recompensas (se cargará desde la base de datos)
        self.default_daily_rewards = []
        self.galaxy_explorer_reward = {
            "amount": 25, 
            "currency": "credits", 
            "type": "galaxy_credits",
            "description": "Galaxy Explorer Bonus"
        }

    def _safe_json_loads(self, data, default=None):
        """Safely parse JSON data that might already be a dict or a string"""
        if data is None:
            return default if default is not None else {}
        
        if isinstance(data, dict):
            return data
        elif isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return default if default is not None else {}
        else:
            return default if default is not None else {}

    async def _load_reward_configs(self):
        """Loads reward configurations from the database"""
        try:
            # Get active configurations from reward_configs table
            response = self.supabase.table("reward_configs").select("*").eq("is_active", True).order("day_number").execute()
            
            if response.data:
                # Convert database data to expected format
                self.default_daily_rewards = []
                for config in response.data:
                    # Only include configurations with valid day_number (1-7)
                    day_number = config.get("day_number")
                    if day_number and 1 <= day_number <= 7:
                        reward_data = config.get("reward_data", {})
                        reward_obj = {
                            "day": day_number,
                            "amount": reward_data.get("amount", 50),
                            "currency": "credits",
                            "type": reward_data.get("type", "credits")
                        }
                        
                        # Add image_url if exists
                        if reward_data.get("image_url"):
                            reward_obj["image_url"] = reward_data.get("image_url")
                        
                        self.default_daily_rewards.append(reward_obj)
                print(f"✅ Loaded {len(self.default_daily_rewards)} daily reward configs from database")
            else:
                # Fallback to default configuration if no data
                self.default_daily_rewards = [
                    {"day": 1, "amount": 50, "currency": "credits", "type": "credits"},
                    {"day": 2, "amount": 75, "currency": "credits", "type": "credits"},
                    {"day": 3, "amount": 100, "currency": "credits", "type": "mystery_nft"},
                    {"day": 4, "amount": 125, "currency": "credits", "type": "credits"},
                    {"day": 5, "amount": 150, "currency": "credits", "type": "credits"},
                    {"day": 6, "amount": 200, "currency": "credits", "type": "credits"},
                    {"day": 7, "amount": 500, "currency": "credits", "type": "premium_mystery_variant"}
                ]
                print("⚠️ Using fallback reward configs (no data in database)")
                
        except Exception as e:
            print(f"❌ Error loading reward configs: {e}")
            # Fallback to default configuration
            self.default_daily_rewards = [
                {"day": 1, "amount": 50, "currency": "credits", "type": "credits"},
                {"day": 2, "amount": 75, "currency": "credits", "type": "credits"},
                {"day": 3, "amount": 100, "currency": "credits", "type": "mystery_nft"},
                {"day": 4, "amount": 125, "currency": "credits", "type": "credits"},
                {"day": 5, "amount": 150, "currency": "credits", "type": "credits"},
                {"day": 6, "amount": 200, "currency": "credits", "type": "credits"},
                {"day": 7, "amount": 500, "currency": "credits", "type": "premium_mystery_variant"}
            ]
            print("⚠️ Using fallback reward configs due to error")

    async def initialize_user_profile(self, user_id: UUID) -> None:
        """Initializes the user profile with streak data if it doesn't exist"""
        try:
            # Check if profile already exists
            existing = self.supabase.table("astrade_user_profiles").select("*").eq("user_id", str(user_id)).execute()
            
            if not existing.data:
                # Create profile with initialized streaks
                profile_data = {
                    "user_id": str(user_id),
                    "level": 1,
                    "experience": 0,
                    "total_trades": 0,
                    "total_pnl": 0,
                    "achievements": json.dumps([]),
                    "streaks": json.dumps({
                        "daily_login": {
                            "current_streak": 0,
                            "longest_streak": 0,
                            "last_activity_date": None
                        },
                        "galaxy_explorer": {
                            "current_streak": 0,
                            "longest_streak": 0,
                            "last_activity_date": None
                        }
                    }),
                    "daily_rewards_claimed": json.dumps([])
                }
                
                self.supabase.table("astrade_user_profiles").insert(profile_data).execute()
            else:
                # If exists, ensure it has streak fields
                profile = existing.data[0]
                if "streaks" not in profile or not profile["streaks"]:
                    self.supabase.table("astrade_user_profiles").update({
                        "streaks": json.dumps({
                            "daily_login": {
                                "current_streak": 0,
                                "longest_streak": 0,
                                "last_activity_date": None
                            },
                            "galaxy_explorer": {
                                "current_streak": 0,
                                "longest_streak": 0,
                                "last_activity_date": None
                            }
                        }),
                        "daily_rewards_claimed": json.dumps([])
                    }).eq("user_id", str(user_id)).execute()
                
        except Exception as e:
            print(f"Error initializing user profile: {e}")

    async def get_daily_rewards_status(self, user_id: UUID) -> DailyRewardResponse:
        """Gets the current status of the user's daily rewards"""
        try:
            today = date.today()
            
            # Load reward configurations
            await self._load_reward_configs()
            
            # Initialize profile if necessary
            await self.initialize_user_profile(user_id)
            
            # Get user profile
            profile_result = self.supabase.table("astrade_user_profiles").select("*").eq("user_id", str(user_id)).execute()
            profile = profile_result.data[0] if profile_result.data else {}
            
            # Get streaks from profile
            streaks = self._safe_json_loads(profile.get("streaks"), {})
            daily_streak = streaks.get("daily_login", {"current_streak": 0, "longest_streak": 0})
            galaxy_streak = streaks.get("galaxy_explorer", {"current_streak": 0, "longest_streak": 0})
            
            # Get rewards claimed today
            claimed_rewards = self._safe_json_loads(profile.get("daily_rewards_claimed"), [])
            claimed_today = any(reward.get("date") == str(today) for reward in claimed_rewards)
            
            # Calculate time until next reward
            next_reward_time = None
            if claimed_today:
                tomorrow = today + timedelta(days=1)
                next_reward_time = f"{(tomorrow - today).days}d"
            
            # Build week rewards
            week_rewards = []
            current_streak = daily_streak["current_streak"]
            
            for i, reward in enumerate(self.default_daily_rewards, 1):
                is_claimed = i <= current_streak
                is_today = i == current_streak + 1 and not claimed_today
                is_locked = i > current_streak + 1
                
                week_rewards.append({
                    "day": i,
                    "reward": reward,
                    "is_claimed": is_claimed,
                    "is_today": is_today,
                    "is_locked": is_locked,
                    "amount": reward["amount"]
                })
            
            return DailyRewardResponse(
                can_claim=not claimed_today,
                current_streak=current_streak,
                longest_streak=daily_streak.get("longest_streak", 0),
                next_reward_in=next_reward_time,
                today_reward=week_rewards[current_streak]["reward"] if current_streak < 7 and not claimed_today else None,
                week_rewards=week_rewards,
                galaxy_explorer_days=galaxy_streak["current_streak"]
            )
            
        except Exception as e:
            print(f"Error getting daily rewards status: {e}")
            return DailyRewardResponse(
                can_claim=False,
                current_streak=0,
                longest_streak=0,
                week_rewards=[]
            )

    async def claim_daily_reward(self, user_id: UUID, reward_type: str = "daily_streak") -> ClaimRewardResponse:
        """Claims the user's daily reward"""
        try:
            today = date.today()
            
            # Load reward configurations
            await self._load_reward_configs()
            
            # Initialize profile if necessary
            await self.initialize_user_profile(user_id)
            
            # Get current profile
            profile_result = self.supabase.table("astrade_user_profiles").select("*").eq("user_id", str(user_id)).execute()
            profile = profile_result.data[0]
            
            # Check if already claimed today
            claimed_rewards = self._safe_json_loads(profile.get("daily_rewards_claimed"), [])
            claimed_today = any(reward.get("date") == str(today) and reward.get("type") == reward_type for reward in claimed_rewards)
            
            if claimed_today:
                return ClaimRewardResponse(
                    success=False,
                    reward_data={},
                    new_streak=0,
                    message="You have already claimed your daily reward"
                )
            
            # Get current streaks
            streaks = self._safe_json_loads(profile.get("streaks"), {})
            daily_streak = streaks.get("daily_login", {"current_streak": 0, "longest_streak": 0})
            
            # Determine reward
            if reward_type == "daily_streak":
                day_number = min(daily_streak["current_streak"] + 1, 7)
                reward_config = self.default_daily_rewards[day_number - 1]
                new_streak = daily_streak["current_streak"] + 1
                
                # Update daily login streak
                streaks["daily_login"] = {
                    "current_streak": new_streak,
                    "longest_streak": max(daily_streak["longest_streak"], new_streak),
                    "last_activity_date": str(today)
                }
            else:  # galaxy_explorer
                reward_config = self.galaxy_explorer_reward
                new_streak = daily_streak["current_streak"] + 1
            
            # Add claimed reward
            claimed_rewards.append({
                "date": str(today),
                "type": reward_type,
                "reward": reward_config,
                "streak_count": new_streak
            })
            
            # If it's an image reward (days 2, 4, 6), add NFT
            if reward_type == "daily_streak" and day_number in [2, 4, 6]:
                image_url = reward_config.get("image_url")
                if image_url:
                    nft_data = {
                        "nft_type": "daily_reward",
                        "nft_name": f"Daily Card {day_number}",
                        "nft_description": f"Reward obtained by completing {day_number} consecutive days",
                        "image_url": image_url,
                        "rarity": "rare" if day_number == 6 else "common",
                        "acquired_from": f"daily_reward_day_{day_number}",
                        "metadata": {
                            "day_number": day_number,
                            "streak_count": new_streak,
                            "reward_type": reward_type
                        }
                    }
                    await self.add_user_nft(user_id, nft_data)
            
            # Calculate new experience
            experience_gained = reward_config.get("amount", 0)
            new_experience = profile.get("experience", 0) + experience_gained
            
            # Calculate new level (every 1000 experience = 1 level)
            new_level = (new_experience // 1000) + 1
            
            # Update profile
            self.supabase.table("astrade_user_profiles").update({
                "experience": new_experience,
                "level": new_level,
                "streaks": json.dumps(streaks),
                "daily_rewards_claimed": json.dumps(claimed_rewards),
                "updated_at": datetime.now().isoformat()
            }).eq("user_id", str(user_id)).execute()
            
            return ClaimRewardResponse(
                success=True,
                reward_data=reward_config,
                new_streak=new_streak,
                message=f"Reward claimed! +{experience_gained} experience (Level {new_level})"
            )
            
        except Exception as e:
            print(f"Error claiming daily reward: {e}")
            return ClaimRewardResponse(
                success=False,
                reward_data={},
                new_streak=0,
                message=f"Error claiming reward: {str(e)}"
            )

    async def record_galaxy_explorer_activity(self, user_id: UUID) -> bool:
        """Records galaxy exploration activity (called when user uses the app)"""
        try:
            today = date.today()
            
            # Initialize profile if necessary
            await self.initialize_user_profile(user_id)
            
            # Get current profile
            profile_result = self.supabase.table("astrade_user_profiles").select("*").eq("user_id", str(user_id)).execute()
            profile = profile_result.data[0]
            
            # Check if already recorded activity today
            claimed_rewards = self._safe_json_loads(profile.get("daily_rewards_claimed"), [])
            claimed_today = any(reward.get("date") == str(today) and reward.get("type") == "galaxy_explorer" for reward in claimed_rewards)
            
            if claimed_today:
                return True  # Already recorded activity today
            
            # Get current streaks
            streaks = self._safe_json_loads(profile.get("streaks"), {})
            galaxy_streak = streaks.get("galaxy_explorer", {"current_streak": 0, "longest_streak": 0})
            
            # Check if it's consecutive day
            last_activity = galaxy_streak.get("last_activity_date")
            is_consecutive = True
            
            if last_activity:
                last_date = datetime.strptime(last_activity, "%Y-%m-%d").date()
                is_consecutive = (today - last_date).days == 1
            
            # Calculate new streak
            new_streak = galaxy_streak["current_streak"] + 1 if is_consecutive else 1
            
            # Add activity reward
            claimed_rewards.append({
                "date": str(today),
                "type": "galaxy_explorer",
                "reward": self.galaxy_explorer_reward,
                "streak_count": new_streak
            })
            
            # Update galaxy explorer streak
            streaks["galaxy_explorer"] = {
                "current_streak": new_streak,
                "longest_streak": max(galaxy_streak["longest_streak"], new_streak),
                "last_activity_date": str(today)
            }
            
            # Update profile
            self.supabase.table("astrade_user_profiles").update({
                "streaks": json.dumps(streaks),
                "daily_rewards_claimed": json.dumps(claimed_rewards),
                "updated_at": datetime.now().isoformat()
            }).eq("user_id", str(user_id)).execute()
            
            return True
            
        except Exception as e:
            print(f"Error recording galaxy explorer activity: {e}")
            return False

    async def get_user_achievements(self, user_id: UUID) -> Dict[str, Any]:
        """Gets the user's achievements related to streaks"""
        try:
            # Initialize profile if necessary
            await self.initialize_user_profile(user_id)
            
            # Get user profile
            profile_result = self.supabase.table("astrade_user_profiles").select("*").eq("user_id", str(user_id)).execute()
            profile = profile_result.data[0] if profile_result.data else {}
            
            # Get streaks from profile
            streaks = self._safe_json_loads(profile.get("streaks"), {})
            daily_streak = streaks.get("daily_login", {"current_streak": 0, "longest_streak": 0})
            galaxy_streak = streaks.get("galaxy_explorer", {"current_streak": 0, "longest_streak": 0})
            
            # Get existing achievements
            existing_achievements = self._safe_json_loads(profile.get("achievements"), [])
            achievements = []
            
            # Daily streak achievements
            if daily_streak["longest_streak"] >= 7:
                achievements.append({
                    "id": "week_warrior",
                    "name": "Weekly Warrior",
                    "description": "Complete 7 consecutive login days",
                    "unlocked": True,
                    "progress": 100,
                    "unlocked_at": datetime.now().isoformat()
                })
            elif daily_streak["current_streak"] > 0:
                achievements.append({
                    "id": "week_warrior",
                    "name": "Weekly Warrior",
                    "description": "Complete 7 consecutive login days",
                    "unlocked": False,
                    "progress": int((daily_streak["current_streak"] / 7) * 100)
                })
            
            # Galaxy explorer achievements
            if galaxy_streak["longest_streak"] >= 30:
                achievements.append({
                    "id": "galaxy_master",
                    "name": "Master of the Galaxy",
                    "description": "Explore the galaxy for 30 consecutive days",
                    "unlocked": True,
                    "progress": 100,
                    "unlocked_at": datetime.now().isoformat()
                })
            elif galaxy_streak["current_streak"] > 0:
                achievements.append({
                    "id": "galaxy_master",
                    "name": "Master of the Galaxy",
                    "description": "Explore the galaxy for 30 consecutive days",
                    "unlocked": False,
                    "progress": int((galaxy_streak["current_streak"] / 30) * 100)
                })
            
            # Update achievements in profile if there are new ones
            if len(achievements) > len(existing_achievements):
                self.supabase.table("astrade_user_profiles").update({
                    "achievements": json.dumps(achievements),
                    "updated_at": datetime.now().isoformat()
                }).eq("user_id", str(user_id)).execute()
            
            return {
                "achievements": achievements,
                "daily_streak": daily_streak,
                "galaxy_streak": galaxy_streak,
                "level": profile.get("level", 1),
                "experience": profile.get("experience", 0),
                "total_trades": profile.get("total_trades", 0)
            }
            
        except Exception as e:
            print(f"Error getting user achievements: {e}")
            return {"achievements": [], "daily_streak": {}, "galaxy_streak": {}}

    async def get_user_profile_with_rewards(self, user_id: UUID) -> Dict[str, Any]:
        """Gets the complete user profile with reward information"""
        try:
            # Initialize profile if necessary
            await self.initialize_user_profile(user_id)
            
            # Get user profile
            profile_result = self.supabase.table("astrade_user_profiles").select("*").eq("user_id", str(user_id)).execute()
            profile = profile_result.data[0] if profile_result.data else {}
            
            # Get streaks from profile
            streaks = self._safe_json_loads(profile.get("streaks"), {})
            daily_streak = streaks.get("daily_login", {"current_streak": 0, "longest_streak": 0})
            galaxy_streak = streaks.get("galaxy_explorer", {"current_streak": 0, "longest_streak": 0})
            
            # Get recently claimed rewards
            claimed_rewards = self._safe_json_loads(profile.get("daily_rewards_claimed"), [])
            recent_rewards = claimed_rewards[-10:] if len(claimed_rewards) > 10 else claimed_rewards
            
            return {
                "user_id": profile.get("user_id"),
                "display_name": profile.get("display_name"),
                "avatar_url": profile.get("avatar_url"),
                "level": profile.get("level", 1),
                "experience": profile.get("experience", 0),
                "total_trades": profile.get("total_trades", 0),
                "total_pnl": profile.get("total_pnl", 0),
                "achievements": self._safe_json_loads(profile.get("achievements"), []),
                "streaks": {
                    "daily_login": daily_streak,
                    "galaxy_explorer": galaxy_streak
                },
                "recent_rewards": recent_rewards,
                "created_at": profile.get("created_at"),
                "updated_at": profile.get("updated_at")
            }
            
        except Exception as e:
            print(f"Error getting user profile with rewards: {e}")
            return {}

    async def add_user_nft(self, user_id: UUID, nft_data: Dict[str, Any]) -> bool:
        """Adds an NFT to the user's collection"""
        try:
            nft_record = {
                "user_id": str(user_id),
                "nft_type": nft_data.get("nft_type", "daily_reward"),
                "nft_name": nft_data.get("nft_name", "NFT"),
                "nft_description": nft_data.get("nft_description"),
                "image_url": nft_data.get("image_url"),
                "rarity": nft_data.get("rarity", "common"),
                "acquired_date": str(date.today()),
                "acquired_from": nft_data.get("acquired_from"),
                "metadata": json.dumps(nft_data.get("metadata", {}))
            }
            
            self.supabase.table("user_nfts").insert(nft_record).execute()
            return True
            
        except Exception as e:
            print(f"Error adding user NFT: {e}")
            return False

    async def get_user_nfts(self, user_id: UUID, nft_type: Optional[str] = None, rarity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Gets the user's NFT collection"""
        try:
            query = self.supabase.table("user_nfts").select("*").eq("user_id", str(user_id))
            
            if nft_type:
                query = query.eq("nft_type", nft_type)
            
            if rarity:
                query = query.eq("rarity", rarity)
            
            response = query.order("acquired_date", desc=True).execute()
            
            if response.data:
                # Parse metadata JSONB
                for nft in response.data:
                    nft["metadata"] = self._safe_json_loads(nft.get("metadata"), {})
            
            return response.data or []
            
        except Exception as e:
            print(f"Error getting user NFTs: {e}")
            return []

    async def get_nft_by_id(self, user_id: UUID, nft_id: UUID) -> Optional[Dict[str, Any]]:
        """Gets a specific NFT from the user"""
        try:
            response = self.supabase.table("user_nfts").select("*").eq("user_id", str(user_id)).eq("id", str(nft_id)).single().execute()
            
            if response.data:
                nft = response.data
                nft["metadata"] = self._safe_json_loads(nft.get("metadata"), {})
                return nft
            
            return None
            
        except Exception as e:
            print(f"Error getting NFT by ID: {e}")
            return None

    async def get_nft_stats(self, user_id: UUID) -> Dict[str, Any]:
        """Gets statistics of the user's NFT collection"""
        try:
            nfts = await self.get_user_nfts(user_id)
            
            stats = {
                "total_nfts": len(nfts),
                "by_type": {},
                "by_rarity": {},
                "recent_acquisitions": []
            }
            
            for nft in nfts:
                # Count by type
                nft_type = nft.get("nft_type", "unknown")
                stats["by_type"][nft_type] = stats["by_type"].get(nft_type, 0) + 1
                
                # Count by rarity
                rarity = nft.get("rarity", "common")
                stats["by_rarity"][rarity] = stats["by_rarity"].get(rarity, 0) + 1
            
            # Recent NFTs (last 5)
            stats["recent_acquisitions"] = sorted(nfts, key=lambda x: x.get("acquired_date", ""), reverse=True)[:5]
            
            return stats
            
        except Exception as e:
            print(f"Error getting NFT stats: {e}")
            return {"total_nfts": 0, "by_type": {}, "by_rarity": {}, "recent_acquisitions": []} 