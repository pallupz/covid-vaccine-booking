package com.indiacowin.cowinotpretriever;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;

import com.android.volley.AuthFailureError;
import com.android.volley.NetworkError;
import com.android.volley.NetworkResponse;
import com.android.volley.NoConnectionError;
import com.android.volley.ParseError;
import com.android.volley.ServerError;
import com.android.volley.TimeoutError;
import com.android.volley.VolleyError;

import org.apache.http.conn.ConnectTimeoutException;
import org.json.JSONException;
import org.xmlpull.v1.XmlPullParserException;

import java.net.ConnectException;
import java.net.MalformedURLException;
import java.net.SocketException;
import java.net.SocketTimeoutException;
import java.util.Objects;

public class VolleyErrorHelper {
    /**
     * Returns appropriate message which is to be displayed to the user
     * against the specified error object.
     */
    public static String getMessage(Object err, Context context) {
        VolleyError error = (VolleyError) err;
        Throwable cause = error.getCause();

        if(error instanceof NoConnectionError){
            ConnectivityManager cm = (ConnectivityManager) context
                    .getSystemService(Context.CONNECTIVITY_SERVICE);
            NetworkInfo activeNetwork = null;
            if (cm != null) {
                activeNetwork = cm.getActiveNetworkInfo();
            }
            if(activeNetwork != null && activeNetwork.isConnectedOrConnecting()){
                return context.getResources().getString(R.string.error_01);
            } else {
                return context.getResources().getString(R.string.error_02);
            }
        }
        else if (error instanceof NetworkError || Objects.requireNonNull(cause) instanceof ConnectException
                || (Objects.requireNonNull(Objects.requireNonNull(cause).getMessage()).contains("connection"))){
            return context.getResources().getString(R.string.error_02);
        }
        else if (Objects.requireNonNull(cause) instanceof MalformedURLException){
            return context.getResources().getString(R.string.error_03);
        }
        else if (error instanceof ParseError || Objects.requireNonNull(cause) instanceof IllegalStateException
                || Objects.requireNonNull(cause) instanceof JSONException
                || Objects.requireNonNull(cause) instanceof XmlPullParserException){
            return context.getResources().getString(R.string.error_04);
        }
        else if (Objects.requireNonNull(cause) instanceof OutOfMemoryError){
            return context.getResources().getString(R.string.error_05);
        }
        else if (error instanceof AuthFailureError){
            return context.getResources().getString(R.string.error_06);
        }
        else if (error instanceof ServerError || Objects.requireNonNull(cause) instanceof ServerError) {
            return context.getResources().getString(R.string.error_07);
        }
        else if (error instanceof TimeoutError || Objects.requireNonNull(cause) instanceof SocketTimeoutException
                || Objects.requireNonNull(cause) instanceof ConnectTimeoutException
                || Objects.requireNonNull(cause) instanceof SocketException
                || (Objects.requireNonNull(
                        Objects.requireNonNull(cause).getMessage()).contains(context.getResources().getString(R.string.error_08)))) {
            return context.getResources().getString(R.string.error_08);
        }
        else {
            NetworkResponse response = error.networkResponse;
            if (response != null) return context.getResources().getString(R.string.error_09, response.statusCode);
            return context.getResources().getString(R.string.error_10);
        }
    }
}