
from .. import models as l_models


class MinerLastInfo:

    @staticmethod
    def update_from_miner(miner: l_models.Miner):
        try:
            miner_last_info = l_models.MinerLastInfo.objects.get(miner_id=miner.miner_id)
            miner_last_info.miner_id = miner.miner_id
            miner_last_info.price_human = miner.price
            miner_last_info.owner = miner.owner
            miner_last_info.buyer = miner.buyer
            miner_last_info.balance_human = miner.balance_human
            miner_last_info.power_human = miner.power_human
            miner_last_info.save()
            return miner_last_info
        except l_models.MinerLastInfo.DoesNotExist:
            return l_models.MinerLastInfo.objects.create(
                miner_id=miner.miner_id,
                price_human=miner.price,
                owner=miner.owner,
                buyer=miner.buyer,
                balance_human=miner.balance_human,
                power_human=miner.power_human
            )

