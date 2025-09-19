from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import re
import os
import tweepy
from src.utils import url_exists, get_newsletter_status, safe_replace_links

class TwitterPostToolInput(BaseModel):
    content: str = Field(..., description="Content of the tweet.")
    devto_url: str = Field(default="", description="Optional Dev.to URL to include in the tweet.")

class TwitterPostTool(BaseTool):
    name: str = "TwitterPostTool"
    description: str = "Posts a tweet to Twitter with optional Dev.to link using Twitter API v2."
    args_schema: Type[BaseModel] = TwitterPostToolInput

    def _extract_devto_url(self, content: str) -> str:
        """Extract Dev.to URL from content if present and validate it"""
        match = re.search(r'(https://dev\.to/[^\s]+)', content)
        if match:
            url = match.group(1)
            # Validate the URL
            if url_exists(url):
                return url
            else:
                return ""  # Return empty if URL is not valid
        return ""

    def _format_tweet_content(self, content: str, devto_url: str = "") -> str:
        """Format tweet content with proper hashtags and Dev.to link with safe checks"""
        # If no Dev.to URL provided, try to extract from content
        if not devto_url:
            devto_url = self._extract_devto_url(content)
        
        # Remove the Dev.to URL from content if it's already there
        content = re.sub(r'https://dev\.to/[^\s]+', '', content).strip()
        
        # Add hashtags
        hashtags = " #AI #Engineering #Scalability #OpenSource"
        
        # Format the tweet with safe link
        if devto_url and url_exists(devto_url):
            tweet = f"{content}\n\n🔗 Read the full article: {devto_url}{hashtags}"
        else:
            tweet = f"{content}{hashtags}"
        
        # Ensure tweet is within Twitter's character limit (280 characters)
        if len(tweet) > 280:
            # Truncate content to fit
            max_content_length = 280 - len(hashtags) - len("\n\n🔗 Read the full article: ") - len(devto_url) - 10  # 10 for safety
            if max_content_length > 0:
                tweet = f"{content[:max_content_length]}...\n\n🔗 Read the full article: {devto_url}{hashtags}"
            else:
                # If still too long, just post the URL with hashtags
                tweet = f"🔗 Read the full article: {devto_url}{hashtags}"
        
        return tweet

    def _authenticate_twitter(self):
        """Authenticate with Twitter API v2"""
        try:
            api_key = os.getenv("TWITTER_API_KEY")
            api_secret = os.getenv("TWITTER_API_SECRET")
            access_token = os.getenv("TWITTER_ACCESS_TOKEN")
            access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
            
            if not all([api_key, api_secret, access_token, access_token_secret]):
                raise ValueError("Missing Twitter API credentials in environment variables")
            
            # Authenticate with Twitter API v2
            auth = tweepy.OAuthHandler(api_key, api_secret)
            auth.set_access_token(access_token, access_token_secret)
            
            # Use API v2 client
            client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            
            return client
            
        except Exception as e:
            raise Exception(f"Twitter authentication failed: {str(e)}")

    def _run(self, content: str, devto_url: str = "") -> str:
        """Post a tweet to Twitter using the Twitter API v2"""
        try:
            # Format the tweet content
            formatted_tweet = self._format_tweet_content(content, devto_url)
            
            print(f"🐦 Preparing to post tweet: {formatted_tweet}")
            print(f"📏 Tweet length: {len(formatted_tweet)} characters")
            
            # Authenticate with Twitter
            client = self._authenticate_twitter()
            
            # Post the tweet using API v2
            response = client.create_tweet(text=formatted_tweet)
            
            if response.data:
                tweet_id = response.data['id']
                tweet_url = f"https://twitter.com/user/status/{tweet_id}"
                
                print(f"✅ Tweet posted successfully!")
                print(f"🔗 Tweet URL: {tweet_url}")
                
                return f"Success! Tweet posted: {formatted_tweet[:100]}...\nTweet URL: {tweet_url}"
            else:
                raise Exception("No response data from Twitter API")
            
        except Exception as e:
            error_msg = f"Error posting tweet: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg 