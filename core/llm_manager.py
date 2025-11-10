"""
LLM Manager for Multi-Model AI Decision Making
Manages multiple LLM models with tool calling capabilities
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from decimal import Decimal

import openai
import httpx
from anthropic import Anthropic

from config.settings import get_settings, LLM_MODELS
from models.database import TradingAccount

logger = logging.getLogger(__name__)

class LLMManager:
    """
    Multi-LLM Manager for AI trading decisions
    Supports multiple models with tool calling through OpenRouter and direct APIs
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.models_config = LLM_MODELS
        
        # Model clients
        self.openrouter_client = None
        self.anthropic_client = None
        
        # Tool registry
        self.available_tools = {}
        
        # Performance tracking
        self.model_stats = {
            model: {"calls": 0, "errors": 0, "avg_time": 0, "total_tokens": 0}
            for model in self.models_config.keys()
        }
        
    async def initialize(self):
        """Initialize LLM clients"""
        logger.info("Initializing LLM Manager")
        
        try:
            # Initialize OpenRouter client
            self.openrouter_client = httpx.AsyncClient(
                base_url="https://openrouter.ai/api/v1",
                headers={
                    "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                    "HTTP-Referer": "https://ai-trading-system.local",
                    "X-Title": "AI Trading System"
                },
                timeout=60.0
            )
            
            # Initialize Anthropic client (optional, for direct API access)
            if hasattr(self.settings, 'anthropic_api_key'):
                self.anthropic_client = Anthropic(
                    api_key=getattr(self.settings, 'anthropic_api_key', '')
                )
            
            logger.info("LLM clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM clients: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown LLM clients"""
        if self.openrouter_client:
            await self.openrouter_client.aclose()
        logger.info("LLM Manager shutdown complete")
    
    async def get_decision_with_tools(
        self, 
        model_name: str, 
        prompt: str, 
        tools: Dict[str, Callable], 
        account: TradingAccount,
        max_tool_calls: int = 5
    ) -> Dict[str, Any]:
        """
        Get LLM decision with tool calling capability
        Equivalent to crypto system's streamText with tools
        """
        start_time = time.time()
        
        try:
            # Register tools for this session
            self.available_tools = tools
            
            # Get model configuration
            model_config = self._get_model_config(account.model_name)
            if not model_config:
                raise ValueError(f"Model {account.model_name} not configured")
            
            # Create tool definitions for the LLM
            tool_definitions = self._create_tool_definitions(tools)
            
            # Make initial LLM call
            response = await self._call_llm_with_tools(
                model_config["name"], 
                prompt, 
                tool_definitions
            )
            
            # Process response and handle tool calls
            processed_response = await self._process_tool_calls(
                response, tools, max_tool_calls
            )
            
            # Calculate metrics
            execution_time = int((time.time() - start_time) * 1000)
            tokens_used = response.get("usage", {}).get("total_tokens", 0)
            
            # Update model statistics
            self._update_model_stats(model_config["name"], execution_time, tokens_used, False)
            
            return {
                "response": processed_response.get("final_response", ""),
                "tool_calls": processed_response.get("tool_calls", []),
                "tokens_used": tokens_used,
                "execution_time_ms": execution_time,
                "model_used": model_config["name"]
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._update_model_stats(model_name, execution_time, 0, True)
            
            logger.error(f"Error in LLM decision making: {e}")
            return {
                "response": f"Error: {str(e)}",
                "tool_calls": [],
                "tokens_used": 0,
                "execution_time_ms": execution_time,
                "model_used": model_name,
                "error": str(e)
            }
    
    async def _call_llm_with_tools(
        self, 
        model_name: str, 
        prompt: str, 
        tool_definitions: List[Dict]
    ) -> Dict[str, Any]:
        """Make LLM API call with tool definitions"""
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert AI trading assistant for Indian stock markets. Use the provided tools to make trading decisions based on market analysis."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
        
        # Prepare request payload
        request_data = {
            "model": model_name,
            "messages": messages,
            "tools": tool_definitions,
            "tool_choice": "auto",
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        # Make API call through OpenRouter
        response = await self.openrouter_client.post(
            "/chat/completions",
            json=request_data
        )
        
        if response.status_code != 200:
            raise Exception(f"LLM API error: {response.status_code} - {response.text}")
        
        return response.json()
    
    async def _process_tool_calls(
        self, 
        llm_response: Dict[str, Any], 
        available_tools: Dict[str, Callable],
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Process tool calls from LLM response
        Handles multiple iterations of tool calling like the crypto system
        """
        
        tool_calls_made = []
        final_response = ""
        iteration = 0
        current_response = llm_response
        
        while iteration < max_iterations:
            message = current_response.get("choices", [{}])[0].get("message", {})
            
            # Check if LLM wants to call tools
            tool_calls = message.get("tool_calls", [])
            
            if not tool_calls:
                # No more tool calls, get final response
                final_response = message.get("content", "")
                break
            
            # Execute tool calls
            tool_results = []
            for tool_call in tool_calls:
                try:
                    function_name = tool_call["function"]["name"]
                    function_args = json.loads(tool_call["function"]["arguments"])
                    
                    if function_name in available_tools:
                        # Execute the tool
                        result = await available_tools[function_name](**function_args)
                        
                        tool_calls_made.append({
                            "tool_name": function_name,
                            "arguments": function_args,
                            "result": result,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        
                        tool_results.append({
                            "tool_call_id": tool_call["id"],
                            "role": "tool",
                            "name": function_name,
                            "content": str(result)
                        })
                        
                    else:
                        error_msg = f"Tool {function_name} not available"
                        tool_results.append({
                            "tool_call_id": tool_call["id"],
                            "role": "tool", 
                            "name": function_name,
                            "content": error_msg
                        })
                        
                except Exception as e:
                    error_msg = f"Error executing {function_name}: {str(e)}"
                    logger.error(error_msg)
                    
                    tool_calls_made.append({
                        "tool_name": function_name,
                        "arguments": function_args,
                        "result": error_msg,
                        "error": True,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    tool_results.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": function_name,
                        "content": error_msg
                    })
            
            # If we executed tools, continue the conversation
            if tool_results:
                # Build follow-up request
                follow_up_messages = [
                    {
                        "role": "system",
                        "content": "You are an expert AI trading assistant. Continue the conversation based on tool results."
                    },
                    {
                        "role": "user",
                        "content": "Please analyze the tool execution results and provide your final trading decision."
                    }
                ]
                
                follow_up_messages.extend(tool_results)
                
                # Make follow-up LLM call
                follow_up_request = {
                    "model": current_response.get("model", "gpt-4-turbo"),
                    "messages": follow_up_messages,
                    "temperature": 0.1,
                    "max_tokens": 1000
                }
                
                follow_up_response = await self.openrouter_client.post(
                    "/chat/completions",
                    json=follow_up_request
                )
                
                if follow_up_response.status_code == 200:
                    current_response = follow_up_response.json()
                else:
                    final_response = f"Error in follow-up: {follow_up_response.text}"
                    break
            else:
                break
            
            iteration += 1
        
        return {
            "final_response": final_response,
            "tool_calls": tool_calls_made,
            "iterations": iteration
        }
    
    def _create_tool_definitions(self, tools: Dict[str, Callable]) -> List[Dict[str, Any]]:
        """Create OpenAI-compatible tool definitions"""
        tool_definitions = []
        
        for tool_name, tool_func in tools.items():
            if tool_name == "buy_stock":
                tool_definitions.append({
                    "type": "function",
                    "function": {
                        "name": "buy_stock",
                        "description": "Buy shares of a stock using a specific strategy",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "Stock symbol (RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK)"
                                },
                                "quantity": {
                                    "type": "integer",
                                    "description": "Number of shares to buy"
                                },
                                "strategy": {
                                    "type": "string", 
                                    "description": "Trading strategy used (vwap, ema, rsi, smc)"
                                }
                            },
                            "required": ["symbol", "quantity", "strategy"]
                        }
                    }
                })
            
            elif tool_name == "sell_stock":
                tool_definitions.append({
                    "type": "function",
                    "function": {
                        "name": "sell_stock",
                        "description": "Sell shares of a stock",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "Stock symbol to sell"
                                },
                                "quantity": {
                                    "type": "integer", 
                                    "description": "Number of shares to sell"
                                },
                                "strategy": {
                                    "type": "string",
                                    "description": "Trading strategy used"
                                }
                            },
                            "required": ["symbol", "quantity", "strategy"]
                        }
                    }
                })
            
            elif tool_name == "close_all_positions":
                tool_definitions.append({
                    "type": "function",
                    "function": {
                        "name": "close_all_positions",
                        "description": "Close all open positions immediately",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                })
            
            elif tool_name == "get_portfolio_status":
                tool_definitions.append({
                    "type": "function",
                    "function": {
                        "name": "get_portfolio_status",
                        "description": "Get current portfolio status and positions",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                })
        
        return tool_definitions
    
    def _get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get model configuration"""
        for config_name, config in self.models_config.items():
            if config["name"] == model_name:
                return config
        return None
    
    def _update_model_stats(self, model_name: str, execution_time: int, tokens: int, error: bool):
        """Update model performance statistics"""
        if model_name in self.model_stats:
            stats = self.model_stats[model_name]
            stats["calls"] += 1
            stats["total_tokens"] += tokens
            
            if error:
                stats["errors"] += 1
            
            # Update average execution time
            if stats["calls"] > 1:
                stats["avg_time"] = (stats["avg_time"] * (stats["calls"] - 1) + execution_time) / stats["calls"]
            else:
                stats["avg_time"] = execution_time
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get performance statistics for all models"""
        return {
            "models": self.model_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def test_model_connection(self, model_name: str) -> Dict[str, Any]:
        """Test connection to a specific model"""
        try:
            start_time = time.time()
            
            response = await self.openrouter_client.post(
                "/chat/completions",
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": "Hello, please respond with 'Connection successful'"}],
                    "max_tokens": 10
                }
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "model": model_name,
                    "response_time_ms": execution_time,
                    "response": response.json()
                }
            else:
                return {
                    "status": "error",
                    "model": model_name,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "model": model_name,
                "error": str(e)
            }