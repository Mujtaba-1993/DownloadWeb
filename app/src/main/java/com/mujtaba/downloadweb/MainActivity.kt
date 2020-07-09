package com.mujtaba.downloadweb

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.webkit.WebView
import kotlinx.android.synthetic.main.activity_main.*

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val webView = WebView(this)
        setContentView(webView)

        webView.loadUrl("https://en.savefrom.net/18/")

        webView.settings.javaScriptEnabled = true

        youtubeBtn.setOnClickListener {
            val intentYoutube = Intent(this, YoutubeActivity::class.java)
            startActivity(intentYoutube)
        }
    }
}
