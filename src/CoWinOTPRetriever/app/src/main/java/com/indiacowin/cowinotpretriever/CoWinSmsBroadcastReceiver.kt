package com.indiacowin.cowinotpretriever

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build
import android.telephony.SmsMessage

class CoWinSmsBroadcastReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context?, intent: Intent?) {

        if("android.provider.Telephony.SMS_RECEIVED" == intent!!.action)
        {
            val extras = intent!!.extras
            if(extras != null)
            {
                val sms = extras.get("pdus") as Array<Any>
                for (i in sms.indices)
                {
                    val smsMessage: SmsMessage = if(Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                        val format = extras.getString("format")
                        SmsMessage.createFromPdu(sms[i] as ByteArray, format)
                    } else {
                        SmsMessage.createFromPdu(sms[i] as ByteArray)
                    }
                    val sender = smsMessage.originatingAddress.toString()
                    val messageBody = smsMessage.messageBody.toString()

                    if(messageBody.contains("CoWIN") && messageBody.contains("OTP"))
                    {
                        sendCoWinSms(context, sender, messageBody)
                    }
                }
            }

        }
    }

    private fun sendCoWinSms(context: Context?, sender: String, sms: String)
    {
        val local = Intent("com.indiacowin.cowinotpretriever.getcowinsms")
        local.putExtra("sender", sender)
        local.putExtra("sms", sms)
        context!!.sendBroadcast(local)
    }
}