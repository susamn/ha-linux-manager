import asyncio
import paramiko
import aiohttp
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPERVISOR_TOKEN = os.getenv("SUPERVISOR_TOKEN")
HA_URL = "http://supervisor/core/api"

async def call_ha_service(domain, service, entity_id):
    url = f"{HA_URL}/services/{domain}/{service}"
    headers = {
        "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"entity_id": entity_id}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status != 200:
                logger.error(f"Error calling HA service: {await response.text()}")
                return False
            return True

async def is_reachable(host):
    try:
        proc = await asyncio.create_subprocess_exec(
            'ping', '-c', '1', '-W', '1', host,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc.wait()
        return proc.returncode == 0
    except Exception as e:
        logger.error(f"Ping error: {e}")
        return False

class ServerManager:
    def __init__(self, name, host, user, password, plug_entity, lock_code=None):
        self.name = name
        self.host = host
        self.user = user
        self.password = password
        self.plug_entity = plug_entity
        self.lock_code = lock_code
        self.status = "Unknown"
        self.is_busy = False

    async def get_status(self):
        if self.is_busy:
            return "Shutting Down"
        if await is_reachable(self.host):
            return "Online"
        return "Offline"

    async def turn_on(self):
        logger.info(f"Turning on {self.name} via {self.plug_entity}")
        return await call_ha_service("switch", "turn_on", self.plug_entity)

    async def turn_off(self):
        if self.is_busy:
            return False, "Process already running"
        
        self.is_busy = True
        try:
            # 1. SSH Shutdown
            logger.info(f"Sending shutdown command to {self.host}")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            try:
                ssh.connect(self.host, username=self.user, password=self.password, timeout=10)
                # Use sudo -S to read password from stdin if needed, 
                # or just shutdown if user has perms.
                # Sending shutdown -h now.
                stdin, stdout, stderr = ssh.exec_command(f"echo {self.password} | sudo -S shutdown -h now")
                # Wait a bit for command to be received
                await asyncio.sleep(2)
                ssh.close()
            except Exception as e:
                self.is_busy = False
                return False, f"SSH Error: {str(e)}"

            # 2. Wait for unreachable
            logger.info(f"Waiting for {self.host} to go offline...")
            max_retries = 24  # 2 minutes (5s intervals)
            for _ in range(max_retries):
                await asyncio.sleep(5)
                if not await is_reachable(self.host):
                    logger.info(f"{self.host} is unreachable. Waiting 10s safety buffer...")
                    await asyncio.sleep(10)
                    # 3. Cut power
                    logger.info(f"Cutting power to {self.plug_entity}")
                    await call_ha_service("switch", "turn_off", self.plug_entity)
                    self.is_busy = False
                    return True, "Shutdown successful"
            
            self.is_busy = False
            return False, "Shutdown timed out (machine still reachable)"
            
        except Exception as e:
            self.is_busy = False
            return False, f"Unexpected error: {str(e)}"
