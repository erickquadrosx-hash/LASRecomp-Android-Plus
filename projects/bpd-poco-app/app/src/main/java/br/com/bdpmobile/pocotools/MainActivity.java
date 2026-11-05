package br.com.bdpmobile.pocotools;

import android.app.Activity;
import android.app.ActivityManager;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.text.InputType;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class MainActivity extends Activity {
    private static final int BG = Color.rgb(12, 19, 32);
    private static final int FG = Color.rgb(235, 242, 255);
    private static final int SUBTLE = Color.rgb(170, 190, 214);
    private static final int ACCENT = Color.rgb(39, 109, 166);
    private EditText packageField;
    private Spinner profileField;
    private TextView profileDetails;

    private int dp(int x) {
        return Math.round(x * getResources().getDisplayMetrics().density);
    }

    private TextView text(String value, float sp, int color) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(sp);
        view.setTextColor(color);
        view.setPadding(0, dp(5), 0, dp(6));
        return view;
    }

    private void add(LinearLayout layout, View v) {
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        params.bottomMargin = dp(8);
        layout.addView(v, params);
    }

    private Button button(LinearLayout layout, String name, View.OnClickListener click) {
        Button b = new Button(this);
        b.setText(name);
        b.setAllCaps(false);
        b.setTextColor(Color.WHITE);
        b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(ACCENT));
        b.setOnClickListener(click);
        add(layout, b);
        return b;
    }

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(BG);
        getWindow().setNavigationBarColor(BG);

        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(BG);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(20), dp(18), dp(20), dp(35));
        scroll.addView(root);
        setContentView(scroll);

        add(root, text("BPD  |  POCO X7 Pro Tools", 25f, FG));
        add(root, text("Auxiliar experimental. Nao e o jogo e nao modifica os graficos internamente.", 14f, SUBTLE));
        add(root, text("DIAGNOSTICO DO APARELHO", 15f, FG));
        add(root, text(deviceReport(), 14f, SUBTLE));

        add(root, text("PACOTE DO BPD MOBILE", 15f, FG));
        packageField = new EditText(this);
        packageField.setSingleLine(true);
        packageField.setTextColor(FG);
        packageField.setHintTextColor(SUBTLE);
        packageField.setHint("ex.: com.exemplo.bdp");
        packageField.setInputType(InputType.TYPE_CLASS_TEXT);
        packageField.setText(getPreferences(0).getString("pkg", ""));
        add(root, packageField);

        button(root, "Localizar o jogo instalado", v -> findGame());
        button(root, "Abrir o jogo", v -> launchGame());

        add(root, text("PERFIL RECOMENDADO", 15f, FG));
        profileField = new Spinner(this);
        String[] options = {"Equilibrado - 30 FPS", "Desempenho - 30 FPS", "Sem escala extra"};
        ArrayAdapter<String> adapter = new ArrayAdapter<>(
            this, android.R.layout.simple_spinner_item, options);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        profileField.setAdapter(adapter);
        profileField.setSelection(Math.max(0, Math.min(2, getPreferences(0).getInt("profile", 0))));
        add(root, profileField);

        profileDetails = text("", 14f, SUBTLE);
        add(root, profileDetails);
        profileField.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            public void onItemSelected(AdapterView<?> parent, View view, int pos, long id) {
                updateProfile();
            }
            public void onNothingSelected(AdapterView<?> parent) {}
        });
        updateProfile();

        button(root, "Copiar comando ADB do perfil", v -> {
            String command = gameCommand(false);
            if (command != null) copy(command);
        });
        button(root, "Copiar comando para restaurar", v -> {
            String command = gameCommand(true);
            if (command != null) copy(command);
        });

        add(root, text("COMO APLICAR", 15f, FG));
        add(root, text(
            "1. Ajuste a resolucao interna pela engrenagem do BPD Mobile.\n" +
            "2. Opcionalmente, copie um comando ADB e execute-o num computador com o celular conectado.\n" +
            "3. O comando e experimental; o HyperOS pode ignora-lo ou rejeita-lo.\n" +
            "4. Teste estabilidade e temperatura; para desfazer, use Restaurar.\n" +
            "O app nao possui root, nao altera driver Mali, nao injeta codigo e nao contem dados do jogo.",
            14f, SUBTLE));
        button(root, "Copiar relatorio do dispositivo", v -> copy(deviceReport()));
    }

    private void updateProfile() {
        int pos = profileField == null ? 0 : profileField.getSelectedItemPosition();
        if (profileDetails == null) return;
        if (pos == 1) {
            profileDetails.setText("Desempenho: escala Android 80%, alvo 30 FPS; no jogo reduza resolucao interna se necessario.");
        } else if (pos == 2) {
            profileDetails.setText("Sem escala extra: restaura ajustes externos. Controle resolucao e FPS no menu do proprio jogo.");
        } else {
            profileDetails.setText("Equilibrado: escala Android 90%, alvo 30 FPS; no jogo comece com 1280 px de largura.");
        }
    }

    private String gameCommand(boolean restore) {
        String pkg = packageField.getText().toString().trim();
        if (!pkg.matches("[A-Za-z_][A-Za-z0-9_]*(\\.[A-Za-z_][A-Za-z0-9_]*)+")) {
            Toast.makeText(this, "Informe um nome de pacote Android valido.", Toast.LENGTH_LONG).show();
            return null;
        }
        if (restore || profileField.getSelectedItemPosition() == 2) {
            return "adb shell cmd game reset " + pkg;
        }
        String scale = profileField.getSelectedItemPosition() == 1 ? "0.8" : "0.9";
        return "adb shell cmd game set --downscale " + scale + " --fps 30 " + pkg;
    }

    private String deviceReport() {
        ActivityManager am = (ActivityManager) getSystemService(Context.ACTIVITY_SERVICE);
        ActivityManager.MemoryInfo mem = new ActivityManager.MemoryInfo();
        if (am != null) am.getMemoryInfo(mem);
        long gb = mem.totalMem / (1024L * 1024L * 1024L);
        String soc = Build.VERSION.SDK_INT >= 31 ? Build.SOC_MODEL : Build.HARDWARE;
        boolean vulkan = getPackageManager().hasSystemFeature("android.hardware.vulkan.level");
        return "Fabricante: " + Build.MANUFACTURER +
            "\nModelo: " + Build.MODEL +
            "\nSoC: " + soc +
            "\nAndroid: " + Build.VERSION.RELEASE +
            "\nRAM aproximada: " + gb + " GiB" +
            "\nVulkan anunciado pelo sistema: " + (vulkan ? "sim" : "nao detectado") +
            "\nPerfil de referencia: Dimensity 8400-Ultra / Mali-G720" +
            "\nPacote selecionado: " +
            (packageField == null ? "(nenhum)" : packageField.getText().toString().trim());
    }

    private void copy(String value) {
        ClipboardManager manager =
            (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        if (manager == null) return;
        manager.setPrimaryClip(ClipData.newPlainText("BPD Tools", value));
        Toast.makeText(this, "Copiado. Execute somente se reconhecer o comando.", Toast.LENGTH_LONG).show();
    }

    private void findGame() {
        PackageManager pm = getPackageManager();
        Intent query = new Intent(Intent.ACTION_MAIN);
        query.addCategory(Intent.CATEGORY_LAUNCHER);
        List<ResolveInfo> matches = pm.queryIntentActivities(query, 0);
        ArrayList<String> labels = new ArrayList<>();
        ArrayList<String> packages = new ArrayList<>();
        for (ResolveInfo item : matches) {
            if (item.activityInfo == null) continue;
            String pkg = item.activityInfo.packageName;
            CharSequence name = item.loadLabel(pm);
            String label = name == null ? "" : name.toString();
            String test = (label + " " + pkg).toLowerCase(Locale.ROOT);
            if (test.contains("diamond") || test.contains("bpd") ||
                test.contains("bdsp") || test.contains("pokemon") ||
                test.contains("pokémon") || test.contains("brilliant")) {
                if (!packages.contains(pkg)) {
                    labels.add(label + "\n" + pkg);
                    packages.add(pkg);
                }
            }
        }
        if (packages.isEmpty()) {
            new AlertDialog.Builder(this).setTitle("Jogo nao encontrado")
                .setMessage("Digite manualmente o identificador do pacote do BPD Mobile no campo acima.")
                .setPositiveButton("Entendi", null).show();
            return;
        }
        new AlertDialog.Builder(this)
            .setTitle("Escolher aplicativo")
            .setItems(labels.toArray(new String[0]), (dialog, index) -> {
                packageField.setText(packages.get(index));
                Toast.makeText(this, "Pacote selecionado.", Toast.LENGTH_SHORT).show();
            }).show();
    }

    private void launchGame() {
        String pkg = packageField.getText().toString().trim();
        Intent intent = getPackageManager().getLaunchIntentForPackage(pkg);
        if (intent == null) {
            Toast.makeText(this, "App nao localizado. Verifique o pacote.", Toast.LENGTH_LONG).show();
            return;
        }
        try {
            startActivity(intent);
        } catch (Exception error) {
            Toast.makeText(this, "Nao foi possivel abrir o jogo.", Toast.LENGTH_LONG).show();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (packageField != null && profileField != null) {
            getPreferences(0).edit()
                .putString("pkg", packageField.getText().toString().trim())
                .putInt("profile", profileField.getSelectedItemPosition()).apply();
        }
    }
}
