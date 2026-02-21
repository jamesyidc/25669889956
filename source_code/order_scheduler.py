#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订单调度中心 - Order Scheduler
处理多账户并发下单请求，确保所有订单都能成功执行
"""

import time
import threading
import queue
import json
import os
import ccxt
from datetime import datetime
from pathlib import Path

# 全局订单队列
order_queue = queue.Queue()

# 订单处理锁（每个账户一个锁，避免同一账户并发下单）
account_locks = {}
lock_manager = threading.Lock()

# 日志目录
LOG_DIR = Path(__file__).parent.parent / 'data' / 'order_scheduler_logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    # 写入日志文件
    log_file = LOG_DIR / f"scheduler_{datetime.now().strftime('%Y%m%d')}.log"
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    except Exception as e:
        print(f"⚠️  写入日志文件失败: {e}")


def get_account_lock(account_id):
    """获取账户锁"""
    with lock_manager:
        if account_id not in account_locks:
            account_locks[account_id] = threading.Lock()
        return account_locks[account_id]


class OrderRequest:
    """订单请求对象"""
    def __init__(self, account_id, symbol, side, order_type, amount, 
                 price=None, leverage=None, strategy_name=None, 
                 callback=None, metadata=None):
        self.request_id = f"{account_id}_{int(time.time()*1000)}"
        self.account_id = account_id
        self.symbol = symbol
        self.side = side  # 'buy' or 'sell'
        self.order_type = order_type  # 'market' or 'limit'
        self.amount = amount
        self.price = price
        self.leverage = leverage
        self.strategy_name = strategy_name or 'unknown'
        self.callback = callback
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.status = 'pending'  # pending, processing, success, failed
        self.result = None
        self.error = None


class OrderScheduler:
    """订单调度中心"""
    
    def __init__(self):
        self.running = False
        self.worker_thread = None
        self.exchanges = {}  # {account_id: exchange_instance}
        
    def start(self):
        """启动调度中心"""
        if self.running:
            log("⚠️  调度中心已经在运行")
            return
            
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        log("✅ 订单调度中心已启动")
        
    def stop(self):
        """停止调度中心"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        log("🛑 订单调度中心已停止")
        
    def submit_order(self, order_request):
        """提交订单请求"""
        log(f"📥 收到订单请求: {order_request.request_id} | "
            f"账户={order_request.account_id} | "
            f"交易对={order_request.symbol} | "
            f"方向={order_request.side} | "
            f"数量={order_request.amount} | "
            f"策略={order_request.strategy_name}")
        
        order_queue.put(order_request)
        return order_request.request_id
        
    def _worker(self):
        """工作线程 - 处理订单队列"""
        log("🔄 订单处理工作线程已启动")
        
        while self.running:
            try:
                # 从队列获取订单请求（超时1秒）
                try:
                    order_request = order_queue.get(timeout=1)
                except queue.Empty:
                    continue
                    
                # 处理订单
                self._process_order(order_request)
                
                # 标记任务完成
                order_queue.task_done()
                
            except Exception as e:
                log(f"❌ 工作线程异常: {e}")
                time.sleep(1)
                
        log("🔄 订单处理工作线程已停止")
        
    def _process_order(self, order_request):
        """处理单个订单"""
        account_id = order_request.account_id
        
        # 获取账户锁（确保同一账户的订单串行执行）
        account_lock = get_account_lock(account_id)
        
        with account_lock:
            log(f"🔒 获取账户锁: {account_id} | 订单ID={order_request.request_id}")
            
            try:
                order_request.status = 'processing'
                
                # 获取交易所实例
                exchange = self._get_exchange(account_id)
                if not exchange:
                    raise Exception(f"无法获取账户 {account_id} 的交易所实例")
                
                # 设置杠杆（如果需要）
                if order_request.leverage:
                    try:
                        exchange.set_leverage(
                            order_request.leverage,
                            order_request.symbol
                        )
                        log(f"⚙️  设置杠杆: {order_request.leverage}x")
                    except Exception as e:
                        log(f"⚠️  设置杠杆失败: {e}")
                
                # 执行下单
                start_time = time.time()
                
                if order_request.order_type == 'market':
                    # 市价单
                    result = exchange.create_order(
                        symbol=order_request.symbol,
                        type='market',
                        side=order_request.side,
                        amount=order_request.amount
                    )
                else:
                    # 限价单
                    result = exchange.create_order(
                        symbol=order_request.symbol,
                        type='limit',
                        side=order_request.side,
                        amount=order_request.amount,
                        price=order_request.price
                    )
                
                elapsed_time = time.time() - start_time
                
                # 记录成功
                order_request.status = 'success'
                order_request.result = result
                
                log(f"✅ 订单执行成功: {order_request.request_id} | "
                    f"耗时={elapsed_time:.2f}s | "
                    f"订单ID={result.get('id', 'N/A')}")
                
                # 保存执行记录
                self._save_execution_log(order_request, result)
                
                # 调用回调函数
                if order_request.callback:
                    try:
                        order_request.callback(True, result, None)
                    except Exception as e:
                        log(f"⚠️  回调函数执行异常: {e}")
                        
            except Exception as e:
                # 记录失败
                order_request.status = 'failed'
                order_request.error = str(e)
                
                log(f"❌ 订单执行失败: {order_request.request_id} | 错误={e}")
                
                # 调用回调函数
                if order_request.callback:
                    try:
                        order_request.callback(False, None, str(e))
                    except Exception as callback_error:
                        log(f"⚠️  回调函数执行异常: {callback_error}")
                        
            finally:
                log(f"🔓 释放账户锁: {account_id}")
                
    def _get_exchange(self, account_id):
        """获取交易所实例"""
        if account_id in self.exchanges:
            return self.exchanges[account_id]
            
        # 加载账户配置
        try:
            config_path = Path(__file__).parent.parent / 'config' / 'okx_accounts.json'
            if not config_path.exists():
                log(f"❌ 配置文件不存在: {config_path}")
                return None
                
            with open(config_path, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
                
            # 查找账户
            account = None
            for acc in accounts:
                if acc.get('id') == account_id:
                    account = acc
                    break
                    
            if not account:
                log(f"❌ 未找到账户: {account_id}")
                return None
                
            # 创建交易所实例
            exchange = ccxt.okx({
                'apiKey': account['apiKey'],
                'secret': account['secret'],
                'password': account['password'],
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'swap'
                }
            })
            
            self.exchanges[account_id] = exchange
            log(f"✅ 创建交易所实例: {account_id}")
            return exchange
            
        except Exception as e:
            log(f"❌ 加载账户配置失败: {e}")
            return None
            
    def _save_execution_log(self, order_request, result):
        """保存执行日志"""
        try:
            log_data = {
                'request_id': order_request.request_id,
                'timestamp': datetime.now().isoformat(),
                'account_id': order_request.account_id,
                'symbol': order_request.symbol,
                'side': order_request.side,
                'order_type': order_request.order_type,
                'amount': order_request.amount,
                'price': order_request.price,
                'leverage': order_request.leverage,
                'strategy_name': order_request.strategy_name,
                'status': order_request.status,
                'order_id': result.get('id') if result else None,
                'metadata': order_request.metadata
            }
            
            log_file = LOG_DIR / f"executions_{datetime.now().strftime('%Y%m%d')}.jsonl"
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + '\n')
                
        except Exception as e:
            log(f"⚠️  保存执行日志失败: {e}")


# 全局调度器实例
_global_scheduler = None
_scheduler_lock = threading.Lock()


def get_scheduler():
    """获取全局调度器实例（单例模式）"""
    global _global_scheduler
    
    with _scheduler_lock:
        if _global_scheduler is None:
            _global_scheduler = OrderScheduler()
            _global_scheduler.start()
        return _global_scheduler


def submit_order_async(account_id, symbol, side, order_type, amount, 
                       price=None, leverage=None, strategy_name=None,
                       callback=None, metadata=None):
    """
    异步提交订单（推荐使用）
    
    参数:
        account_id: 账户ID
        symbol: 交易对，如 'BTC/USDT:USDT'
        side: 'buy' 或 'sell'
        order_type: 'market' 或 'limit'
        amount: 数量
        price: 价格（限价单必需）
        leverage: 杠杆倍数
        strategy_name: 策略名称
        callback: 回调函数 callback(success, result, error)
        metadata: 额外元数据
        
    返回:
        request_id: 请求ID
    """
    scheduler = get_scheduler()
    
    order_request = OrderRequest(
        account_id=account_id,
        symbol=symbol,
        side=side,
        order_type=order_type,
        amount=amount,
        price=price,
        leverage=leverage,
        strategy_name=strategy_name,
        callback=callback,
        metadata=metadata
    )
    
    return scheduler.submit_order(order_request)


# 测试代码
if __name__ == '__main__':
    print("🚀 订单调度中心测试")
    print("=" * 60)
    
    # 启动调度器
    scheduler = get_scheduler()
    
    # 定义回调函数
    def order_callback(success, result, error):
        if success:
            print(f"✅ 订单成功: {result}")
        else:
            print(f"❌ 订单失败: {error}")
    
    # 提交测试订单
    request_id = submit_order_async(
        account_id='account_main',
        symbol='BTC/USDT:USDT',
        side='buy',
        order_type='market',
        amount=0.001,
        leverage=10,
        strategy_name='test_strategy',
        callback=order_callback
    )
    
    print(f"📝 提交订单: {request_id}")
    
    # 等待处理完成
    time.sleep(5)
    
    print("\n✅ 测试完成")
