package com.example.jd

import android.Manifest
import android.annotation.SuppressLint
import android.content.*
import android.os.Bundle
import android.speech.RecognizerIntent
import android.speech.tts.TextToSpeech
import android.webkit.JavascriptInterface
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import java.util.*

@Suppress("DEPRECATION")
class MainActivity : AppCompatActivity(), TextToSpeech.OnInitListener {

    private lateinit var webView: WebView
    private lateinit var tts: TextToSpeech
    private val REQUEST_CODE_SPEECH_INPUT = 100

    private lateinit var sharedPreferences: SharedPreferences
    private val PREF_NAME = "JD_PREFS"
    private val LOGGED_IN_KEY = "logged_in"

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        sharedPreferences = getSharedPreferences(PREF_NAME, MODE_PRIVATE)

        webView = findViewById(R.id.webview)
        tts = TextToSpeech(this, this)

        webView.settings.javaScriptEnabled = true
        webView.webViewClient = WebViewClient()
        webView.addJavascriptInterface(WebAppInterface(this), "AndroidJD")

        val isLoggedIn = sharedPreferences.getBoolean(LOGGED_IN_KEY, false)
        if (isLoggedIn) {
            webView.loadUrl("https://jd-9900.onrender.com/")
        } else {
            webView.loadUrl("https://jd-9900.onrender.com/login")
        }

        ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.RECORD_AUDIO), 1)
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            tts.language = Locale.US
        } else {
            Toast.makeText(this, "TTS initialization failed", Toast.LENGTH_SHORT).show()
        }
    }

    inner class WebAppInterface(private val context: Context) {

        @JavascriptInterface
        fun startVoice() {
            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
                putExtra(RecognizerIntent.EXTRA_PROMPT, "Speak your command...")
            }
            try {
                startActivityForResult(intent, REQUEST_CODE_SPEECH_INPUT)
            } catch (_: ActivityNotFoundException) {
                Toast.makeText(context, "Speech recognition not supported", Toast.LENGTH_SHORT).show()
            }
        }

        @JavascriptInterface
        fun speakResponse(text: String) {
            runOnUiThread {
                tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, null)
            }
        }

        @JavascriptInterface
        fun openYouTube(song: String) {
            val intent = Intent(Intent.ACTION_SEARCH).apply {
                setPackage("com.google.android.youtube")
                putExtra("query", song)
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            try {
                startActivity(intent)
            } catch (_: ActivityNotFoundException) {
                Toast.makeText(context, "YouTube app not found", Toast.LENGTH_SHORT).show()
            }
        }

        @SuppressLint("UseKtx")
        @JavascriptInterface
        fun onLoginSuccess() {
            val editor = sharedPreferences.edit()
            editor.putBoolean(LOGGED_IN_KEY, true)
            editor.apply()
        }

        @SuppressLint("UseKtx")
        @JavascriptInterface
        fun onLogout() {
            val editor = sharedPreferences.edit()
            editor.clear()
            editor.apply()

            runOnUiThread {
                webView.loadUrl("https://jd-9900.onrender.com/login")
            }
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_CODE_SPEECH_INPUT && resultCode == RESULT_OK && data != null) {
            val result = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            val spokenText = result?.get(0) ?: ""
            webView.evaluateJavascript(
                "document.getElementById('command').value = '$spokenText'; sendCommand();",
                null
            )
        }
    }

    override fun onDestroy() {
        tts.stop()
        tts.shutdown()
        super.onDestroy()
    }
}






