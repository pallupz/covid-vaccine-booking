package com.indiacowin.cowinotpretriever

import android.Manifest
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.os.Bundle
import android.text.method.KeyListener
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.SwitchCompat
import androidx.core.app.ActivityCompat
import com.android.volley.RequestQueue
import com.android.volley.toolbox.StringRequest
import com.android.volley.toolbox.Volley

class MainActivity : AppCompatActivity() {

    companion object {
        private const val REQUEST_RECEIVE_SMS = 2
    }

    private lateinit var mCoWinSmsBroadcastReceiver: CoWinSmsBroadcastReceiver
    private lateinit var mMainActivityReceiver: BroadcastReceiver
    private lateinit var mRequestQueue: RequestQueue
    private lateinit var mKvdbUrl: String

    private lateinit var mPhoneNumberEntry: EditText
    private lateinit var mKeyListener: KeyListener
    private lateinit var mStatusTextView: TextView
    private lateinit var mStartListeningCowinOtpSwitch: SwitchCompat
    private var mReceiverIsActive: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // get read sms permission
        getReadSmsPermission()

        // initialize CoWIN sms broadcast receiver
        mCoWinSmsBroadcastReceiver = CoWinSmsBroadcastReceiver()

        // initialize broadcast receiver for receiving CoWIN sms in main activity
        val intentFilter = IntentFilter("com.indiacowin.cowinotpretriever.getcowinsms")
        mMainActivityReceiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context?, intent: Intent?) {
                // make status update here
                if (intent != null)
                {
                    val sender = intent!!.getStringExtra("sender").toString()
                    val sms = intent!!.getStringExtra("sms").toString()
                    onOTPReceived(sender, sms)
                }
            }
        }
        registerReceiver(mMainActivityReceiver, intentFilter)

        // initialize simple request queue
        mRequestQueue = Volley.newRequestQueue(this)

        // initialize ui elements so we can use it later
        mPhoneNumberEntry = findViewById(R.id.PhoneNumberEntry)
        mKeyListener = mPhoneNumberEntry.keyListener
        mStatusTextView = findViewById(R.id.StatusTextView)
        mStartListeningCowinOtpSwitch = findViewById(R.id.StartListeningCowinOtpSwitch)
        mStartListeningCowinOtpSwitch.setOnCheckedChangeListener{ _, isChecked ->
            if(isChecked)
            {
                startSMSListener()
            }
            else
            {
                endSMSListener()
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        // Unregister main activity receiver
        unregisterReceiver(mMainActivityReceiver)

        // unregister cowin sms receiver
        if(mReceiverIsActive) {
            unregisterReceiver(mCoWinSmsBroadcastReceiver)
            mReceiverIsActive = false
        }
    }

    private fun getReadSmsPermission() {
        // check if receive sms permission exists
        if(ActivityCompat.checkSelfPermission(this, Manifest.permission.RECEIVE_SMS) != PackageManager.PERMISSION_GRANTED)
        {
            // request permission for receiving sms
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.RECEIVE_SMS), REQUEST_RECEIVE_SMS)
        }
    }

    private fun startSMSListener() {
        // disable phone number entry
        mPhoneNumberEntry.keyListener = null

        // initialize sms retrieved intent filter
        val intentFilter = IntentFilter("android.provider.Telephony.SMS_RECEIVED")

        // register broadcast receiver
        registerReceiver(mCoWinSmsBroadcastReceiver, intentFilter)

        // mark receiver as active
        mReceiverIsActive = true

        // set url for sending the cowin otp sms
        mKvdbUrl = "${resources.getString(R.string.kvdb_base_url)}${mPhoneNumberEntry.text}"
        mStatusTextView.text = "Sending CoWIN OTP sms to $mKvdbUrl"
        Toast.makeText(this, "CoWIN SMS Retriever has started", Toast.LENGTH_LONG).show()
    }

    private fun endSMSListener() {
        // enable phone number entry
        mPhoneNumberEntry.keyListener = mKeyListener

        // mark receiver as inactive
        mReceiverIsActive = false

        // unregister broadcast receiver
        unregisterReceiver(mCoWinSmsBroadcastReceiver)

        mStatusTextView.text = "Stopped reading sms"
        Toast.makeText(this, "CoWIN SMS Retriever has stopped", Toast.LENGTH_LONG).show()
    }

    private fun onOTPReceived(sender: String, sms: String) {
        Toast.makeText(this, "Sending request to $mKvdbUrl from CoWIN: $sender", Toast.LENGTH_LONG).show()
        // request a string response from the provided URL.
        val stringRequest = object : StringRequest(
            Method.PUT,
            mKvdbUrl,
            { response ->
                val trimmedResponse = if(response.length > 500) { response.substring(0, 500) } else { response }
                // Display the first 500 characters of the response string.
                mStatusTextView.text = "Successfully sent CoWIN OTP: $trimmedResponse"
            },
            { response -> mStatusTextView.text = "Failed to send CoWIN OTP sms to $mKvdbUrl: ${response.message}" })
        {
            override fun getBody(): ByteArray {
                return sms.toByteArray(Charsets.UTF_8)
            }

            override fun getBodyContentType(): String {
                return "text/plain; charset=utf-8"
            }

            override fun getHeaders(): MutableMap<String, String> {
                val headers = HashMap<String, String>()
                headers["Content-Type"] = "text/plain"
                headers["charset"] = "utf-8"
                return headers
            }
        }
        // add the request to the RequestQueue.
        mRequestQueue.add(stringRequest)
    }
}