import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:progress_hub/pages/login_page.dart';
import 'package:progress_hub/pages/mainScreen.dart';
import 'firebase_options.dart';
import 'package:firebase_auth/firebase_auth.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(context) {
    return MaterialApp(
      theme: ThemeData().copyWith(
        useMaterial3: true,
        colorScheme:
            ColorScheme.fromSeed(seedColor: Color.fromARGB(255, 63, 17, 177)),
      ),
      home: StreamBuilder(
        stream: FirebaseAuth.instance.authStateChanges(),
        builder: (context, snapshot) {
          if(snapshot.connectionState){
            
          }
          if (snapshot.hasData) {
            return const mainScreen();
          } else {
            return const AuthScreen();
          }
        },
      ),
    );
  }
}
